"""Servidor gRPC: adaptador de entrada da estratégia gRPC (contrato em communication/grpc/proto)."""
from __future__ import annotations

import grpc

import ecommerce_pb2
import ecommerce_pb2_grpc
from estoque.application.ports.inbound import ReleaseStockCommand, ReserveStockCommand
from estoque.application.use_cases.release_stock import ReleaseStockUseCase
from estoque.application.use_cases.reserve_stock import ReserveStockUseCase
from estoque.domain.exceptions import InsufficientStockError, ProductNotFoundError
from estoque.infrastructure.database.session_scope import repository_scope
from estoque.infrastructure.metrics import track


class StockServicer(ecommerce_pb2_grpc.StockServiceServicer):
    def __init__(self, state) -> None:
        self._state = state

    async def ReserveStock(self, request, context):
        with track("GRPC", "/ecommerce.StockService/ReserveStock") as obs:
            async with repository_scope(self._state) as repo:
                try:
                    await ReserveStockUseCase(repo).execute(
                        ReserveStockCommand(product_id=request.product_id, quantity=request.quantity)
                    )
                except ProductNotFoundError as exc:
                    obs.status = "404"
                    await context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
                except InsufficientStockError as exc:
                    obs.status = "422"
                    await context.abort(grpc.StatusCode.FAILED_PRECONDITION, str(exc))
            return ecommerce_pb2.StockReservation(
                product_id=request.product_id, quantity=request.quantity, reserved=True
            )

    async def ReleaseStock(self, request, context):
        with track("GRPC", "/ecommerce.StockService/ReleaseStock") as obs:
            async with repository_scope(self._state) as repo:
                try:
                    await ReleaseStockUseCase(repo).execute(
                        ReleaseStockCommand(product_id=request.product_id, quantity=request.quantity)
                    )
                except ProductNotFoundError as exc:
                    obs.status = "404"
                    await context.abort(grpc.StatusCode.NOT_FOUND, str(exc))
            return ecommerce_pb2.StockReleased(released=True)


async def start_grpc_server(state, port: int) -> grpc.aio.Server:
    server = grpc.aio.server()
    ecommerce_pb2_grpc.add_StockServiceServicer_to_server(StockServicer(state), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    return server
