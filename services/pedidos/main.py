from contextlib import asynccontextmanager

import aiohttp
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from pedidos.infrastructure.config import Settings
from pedidos.infrastructure.http.router import router
from pedidos.infrastructure.metrics import MetricsMiddleware

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings
    # Cliente HTTP da estratégia REST. aiohttp em vez de httpx: o httpx tem overhead de CPU
    # alto sob concorrência, o que mediria a biblioteca e não o protocolo.
    app.state.http_client = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=settings.REQUEST_TIMEOUT_S)
    )
    app.state.grpc_stubs = None
    app.state.amqp_rpc = None

    if settings.COMMUNICATION_STRATEGY == "grpc":
        from pedidos.infrastructure.clients.grpc.channels import GrpcStubs
        app.state.grpc_stubs = GrpcStubs.open(
            settings.USUARIO_GRPC_TARGET,
            settings.ESTOQUE_GRPC_TARGET,
            settings.PAGAMENTO_GRPC_TARGET,
        )
    elif settings.COMMUNICATION_STRATEGY == "mensageria":
        from pedidos.infrastructure.clients.amqp.rpc_client import AmqpRpcClient
        app.state.amqp_rpc = await AmqpRpcClient.connect(settings.AMQP_URL, settings.REQUEST_TIMEOUT_S)

    if settings.USE_IN_MEMORY_DB:
        from pedidos.infrastructure.database.in_memory_repository import InMemoryOrderRepository
        app.state.order_repo = InMemoryOrderRepository()
        app.state.session_factory = None
    else:
        from pedidos.infrastructure.database.connection import Base, create_engine_and_session
        from pedidos.infrastructure.database import models as _models  # noqa: F401

        engine, session_factory = create_engine_and_session(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        app.state.order_repo = None  # criado por request via session
        app.state.session_factory = session_factory
        app.state.engine = engine

    yield

    await app.state.http_client.close()
    if app.state.grpc_stubs is not None:
        await app.state.grpc_stubs.close()
    if app.state.amqp_rpc is not None:
        await app.state.amqp_rpc.close()
    if not settings.USE_IN_MEMORY_DB:
        await app.state.engine.dispose()


app = FastAPI(
    title="Pedidos Service",
    description="Microserviço de pedidos — TCC Estratégias de Comunicação entre Microserviços",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(MetricsMiddleware)
app.include_router(router)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok", "service": "pedidos"}


@app.get("/metrics", tags=["infra"], include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
