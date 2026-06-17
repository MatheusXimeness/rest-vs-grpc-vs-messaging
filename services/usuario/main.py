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

    yield

    if not settings.USE_IN_MEMORY_DB:
        await app.state.engine.dispose()


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
