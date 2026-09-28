"""Handlers das filas do serviço de estoque (contrato em communication/messaging/rabbitmq)."""
from __future__ import annotations

from estoque.application.ports.inbound import ReleaseStockCommand, ReserveStockCommand
from estoque.application.use_cases.release_stock import ReleaseStockUseCase
from estoque.application.use_cases.reserve_stock import ReserveStockUseCase
from estoque.domain.exceptions import InsufficientStockError, ProductNotFoundError
from estoque.infrastructure.amqp.rpc_server import start_rpc_server
from estoque.infrastructure.database.session_scope import repository_scope


def _handlers(state) -> dict:
    async def reserve(payload: dict) -> dict:
        command = ReserveStockCommand(product_id=payload["product_id"], quantity=payload["quantity"])
        async with repository_scope(state) as repo:
            try:
                await ReserveStockUseCase(repo).execute(command)
            except ProductNotFoundError as exc:
                return {"status": 404, "detail": str(exc)}
            except InsufficientStockError as exc:
                return {"status": 422, "detail": str(exc)}
        return {
            "status": 200,
            "product_id": command.product_id,
            "quantity": command.quantity,
            "reserved": True,
        }

    # Evento sem resposta: o pedido não espera a liberação terminar.
    async def release(payload: dict) -> dict:
        command = ReleaseStockCommand(product_id=payload["product_id"], quantity=payload["quantity"])
        async with repository_scope(state) as repo:
            try:
                await ReleaseStockUseCase(repo).execute(command)
            except ProductNotFoundError as exc:
                return {"status": 404, "detail": str(exc)}
        return {"status": 200, "released": True}

    return {"estoque.reserve": reserve, "estoque.release": release}


async def start_consumer(state, url: str, prefetch: int):
    return await start_rpc_server(url, _handlers(state), prefetch)
