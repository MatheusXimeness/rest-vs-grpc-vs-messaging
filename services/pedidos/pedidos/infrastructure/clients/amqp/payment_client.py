from decimal import Decimal
from uuid import UUID

from pedidos.application.ports.outbound import IPaymentServicePort, PaymentResult
from pedidos.infrastructure.clients.amqp.rpc_client import AmqpRpcClient, raise_for_status

QUEUE = "pagamento.process"


class PaymentAmqpClient(IPaymentServicePort):
    def __init__(self, rpc: AmqpRpcClient) -> None:
        self._rpc = rpc

    async def process_payment(
        self, order_id: UUID, amount: Decimal, user_id: str
    ) -> PaymentResult:
        reply = await self._rpc.call(
            QUEUE, {"order_id": str(order_id), "amount": str(amount), "user_id": user_id}
        )
        raise_for_status(reply, QUEUE)
        return PaymentResult(
            order_id=UUID(reply["order_id"]),
            approved=reply["approved"],
            transaction_id=reply.get("transaction_id"),
        )
