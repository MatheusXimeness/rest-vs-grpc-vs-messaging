from contextlib import asynccontextmanager

from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from estoque.infrastructure.config import Settings
from estoque.infrastructure.http.router import router
from estoque.infrastructure.metrics import MetricsMiddleware

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings = settings

    if settings.USE_IN_MEMORY_DB:
        from estoque.infrastructure.database.in_memory_repository import InMemoryStockRepository
        app.state.stock_repo = InMemoryStockRepository(settings.INITIAL_STOCK_QUANTITY)
        app.state.session_factory = None
    else:
        from estoque.infrastructure.database.connection import Base, create_engine_and_session
        from estoque.infrastructure.database import models as _models  # noqa: F401

        engine, session_factory = create_engine_and_session(settings.DATABASE_URL)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        app.state.stock_repo = None
        app.state.session_factory = session_factory
        app.state.engine = engine

        await _seed_postgres(session_factory, settings.INITIAL_STOCK_QUANTITY)

    stop_inbound_adapter = await _start_inbound_adapter(app.state, settings)

    yield

    if stop_inbound_adapter is not None:
        await stop_inbound_adapter()

    if not settings.USE_IN_MEMORY_DB:
        await app.state.engine.dispose()


async def _seed_postgres(session_factory, initial_quantity: int | None) -> None:
    from sqlalchemy import select
    from estoque.infrastructure.database.models import StockModel

    async with session_factory() as session:
        result = await session.execute(select(StockModel).limit(1))
        if result.scalar_one_or_none() is not None:
            return

        initial = [
            StockModel(product_id="mouse", product_name="Mouse USB", quantity_available=100, quantity_reserved=0),
            StockModel(product_id="keyboard", product_name="Teclado Mecânico", quantity_available=50, quantity_reserved=0),
            StockModel(product_id="monitor", product_name='Monitor 24"', quantity_available=20, quantity_reserved=0),
            StockModel(product_id="headset", product_name="Headset Gamer", quantity_available=75, quantity_reserved=0),
            StockModel(product_id="webcam", product_name="Webcam HD", quantity_available=30, quantity_reserved=0),
        ]
        for item in initial:
            if initial_quantity is not None:
                item.quantity_available = initial_quantity
            session.add(item)
        await session.commit()


async def _start_inbound_adapter(state, settings):
    """Sobe o adaptador de entrada da estratégia configurada e devolve a função de parada."""
    if settings.COMMUNICATION_STRATEGY == "grpc":
        from estoque.infrastructure.grpc.server import start_grpc_server
        server = await start_grpc_server(state, settings.GRPC_PORT)
        return lambda: server.stop(grace=1)
    if settings.COMMUNICATION_STRATEGY == "mensageria":
        from estoque.infrastructure.amqp.consumer import start_consumer
        connection = await start_consumer(state, settings.AMQP_URL, settings.AMQP_PREFETCH)
        return connection.close
    return None

app = FastAPI(
    title="Estoque Service",
    description="Microserviço de estoque — TCC Estratégias de Comunicação entre Microserviços",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(MetricsMiddleware)
app.include_router(router)


@app.get("/health", tags=["infra"])
async def health():
    return {"status": "ok", "service": "estoque"}


@app.get("/metrics", tags=["infra"], include_in_schema=False)
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
