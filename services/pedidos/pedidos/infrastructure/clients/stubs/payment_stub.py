from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from pedidos.application.ports.outbound import IPaymentServicePort, PaymentResult


class PaymentStubAdapter(IPaymentServicePort):
    async def process_payment(
        self, order_id: UUID, amount: Decimal, user_id: str
    ) -> PaymentResult:
        return PaymentResult(
            order_id=order_id,
            approved=True,
            transaction_id=str(uuid4()),
        )
