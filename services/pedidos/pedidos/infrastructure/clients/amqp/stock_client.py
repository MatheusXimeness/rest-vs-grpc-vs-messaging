import aio_pika

from pedidos.application.ports.outbound import IStockServicePort, StockReservation
from pedidos.domain.exceptions import InsufficientStockError
from pedidos.infrastructure.clients.amqp.rpc_client import AmqpRpcClient, raise_for_status

RESERVE_QUEUE = "estoque.reserve"
RELEASE_QUEUE = "estoque.release"


class StockAmqpClient(IStockServicePort):
    def __init__(self, rpc: AmqpRpcClient) -> None:
        self._rpc = rpc

    async def reserve_stock(self, product_id: str, quantity: int) -> StockReservation:
        reply = await self._rpc.call(RESERVE_QUEUE, {"product_id": product_id, "quantity": quantity})
        if reply["status"] == 404:
            raise InsufficientStockError(f"Product '{product_id}' not found in stock")
        if reply["status"] == 422:
            raise InsufficientStockError(f"Insufficient stock for product '{product_id}'")
        raise_for_status(reply, RESERVE_QUEUE)
        return StockReservation(
            product_id=reply["product_id"],
            quantity=reply["quantity"],
            reserved=reply["reserved"],
        )

    async def release_stock(self, product_id: str, quantity: int) -> None:
        # Evento: o pedido não espera o estoque confirmar a liberação.
        try:
            await self._rpc.publish(RELEASE_QUEUE, {"product_id": product_id, "quantity": quantity})
        except aio_pika.exceptions.AMQPError:
            pass
