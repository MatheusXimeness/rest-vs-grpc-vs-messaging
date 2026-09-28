from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from usuario.infrastructure.config import Settings
from usuario.infrastructure.http.router import router
from usuario.infrastructure.metrics import MetricsMiddleware

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings

    if settings.USE_IN_MEMORY_DB:
        from usuario.infrastructure.database.in_memory_repository import InMemoryUserRepository
        app.state.user_repo = InMemoryUserRepository()
        app.state.session_factory = None
    else:
        from usuario.infrastructure.database.connection import Base, create_engine_and_session
        from usuario.infrastructure.database import models as _models  # noqa: F401

        engine, session_factory = create_engine_and_session(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        app.state.user_repo = None
        app.state.session_factory = session_factory
        app.state.engine = engine

        await _seed_postgres(session_factory)

    stop_inbound_adapter = await _start_inbound_adapter(app.state, settings)

    yield

    if stop_inbound_adapter is not None:
        await stop_inbound_adapter()

    if not settings.USE_IN_MEMORY_DB:
        await app.state.engine.dispose()


async def _seed_postgres(session_factory) -> None:
    from sqlalchemy import select
    from usuario.infrastructure.database.in_memory_repository import _SEED
    from usuario.infrastructure.database.models import UserModel

    async with session_factory() as session:
        result = await session.execute(select(UserModel).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        for user in _SEED:
            session.add(UserModel(id=user.id, name=user.name, email=user.email))
        await session.commit()


async def _start_inbound_adapter(state, settings):
    """Sobe o adaptador de entrada da estratégia configurada e devolve a função de parada."""
    if settings.COMMUNICATION_STRATEGY == "grpc":
        from usuario.infrastructure.grpc.server import start_grpc_server
        server = await start_grpc_server(state, settings.GRPC_PORT)
        return lambda: server.stop(grace=1)
    if settings.COMMUNICATION_STRATEGY == "mensageria":
        from usuario.infrastructure.amqp.consumer import start_consumer
        connection = await start_consumer(state, settings.AMQP_URL, settings.AMQP_PREFETCH)
        return connection.close
    return None

app = FastAPI(
    title="Usuario Service",
    description="Microserviço de usuário — TCC Estratégias de Comunicação entre Microserviços",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(MetricsMiddleware)
app.include_router(router)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok", "service": "usuario"}


@app.get("/metrics", tags=["infra"], include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
