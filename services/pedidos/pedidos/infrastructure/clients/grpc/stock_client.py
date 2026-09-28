import grpc

import ecommerce_pb2
import ecommerce_pb2_grpc
from pedidos.application.ports.outbound import IStockServicePort, StockReservation
from pedidos.domain.exceptions import InsufficientStockError
from pedidos.infrastructure.clients.grpc.errors import raise_for_rpc_error


class StockGrpcClient(IStockServicePort):
    def __init__(self, stub: ecommerce_pb2_grpc.StockServiceStub, timeout: float) -> None:
        self._stub = stub
        self._timeout = timeout

    async def reserve_stock(self, product_id: str, quantity: int) -> StockReservation:
        try:
            reservation = await self._stub.ReserveStock(
                ecommerce_pb2.StockOperation(product_id=product_id, quantity=quantity),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            if exc.code() == grpc.StatusCode.NOT_FOUND:
                raise InsufficientStockError(f"Product '{product_id}' not found in stock") from exc
            if exc.code() == grpc.StatusCode.FAILED_PRECONDITION:
                raise InsufficientStockError(f"Insufficient stock for product '{product_id}'") from exc
            raise_for_rpc_error(exc, "Estoque")

        return StockReservation(
            product_id=reservation.product_id,
            quantity=reservation.quantity,
            reserved=reservation.reserved,
        )

    async def release_stock(self, product_id: str, quantity: int) -> None:
        try:
            await self._stub.ReleaseStock(
                ecommerce_pb2.StockOperation(product_id=product_id, quantity=quantity),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError:
            pass
