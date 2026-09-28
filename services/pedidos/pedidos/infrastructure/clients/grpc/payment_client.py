from decimal import Decimal
from uuid import UUID

import grpc

import ecommerce_pb2
import ecommerce_pb2_grpc
from pedidos.application.ports.outbound import IPaymentServicePort, PaymentResult
from pedidos.infrastructure.clients.grpc.errors import raise_for_rpc_error


class PaymentGrpcClient(IPaymentServicePort):
    def __init__(self, stub: ecommerce_pb2_grpc.PaymentServiceStub, timeout: float) -> None:
        self._stub = stub
        self._timeout = timeout

    async def process_payment(
        self, order_id: UUID, amount: Decimal, user_id: str
    ) -> PaymentResult:
        try:
            payment = await self._stub.ProcessPayment(
                ecommerce_pb2.ProcessPaymentRequest(
                    order_id=str(order_id), user_id=user_id, amount=str(amount)
                ),
                timeout=self._timeout,
            )
        except grpc.aio.AioRpcError as exc:
            raise_for_rpc_error(exc, "Pagamento")

        return PaymentResult(
            order_id=UUID(payment.order_id),
            approved=payment.approved,
            transaction_id=payment.transaction_id or None,
        )
