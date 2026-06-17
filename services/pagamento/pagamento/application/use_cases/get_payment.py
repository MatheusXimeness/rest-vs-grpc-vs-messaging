from __future__ import annotations

from pagamento.application.ports.inbound import (
    GetPaymentByOrderQuery,
    GetPaymentQuery,
    IGetPaymentByOrderUseCase,
    IGetPaymentUseCase,
)
from pagamento.application.ports.outbound import IPaymentRepository
from pagamento.domain.exceptions import PaymentNotFoundError
from pagamento.domain.payment import Payment


class GetPaymentUseCase(IGetPaymentUseCase):
    def __init__(self, repo: IPaymentRepository) -> None:
        self._repo = repo

    async def execute(self, query: GetPaymentQuery) -> Payment:
        payment = await self._repo.find_by_id(query.payment_id)
        if payment is None:
            raise PaymentNotFoundError(f"Payment '{query.payment_id}' not found")
        return payment


class GetPaymentByOrderUseCase(IGetPaymentByOrderUseCase):
    def __init__(self, repo: IPaymentRepository) -> None:
        self._repo = repo

    async def execute(self, query: GetPaymentByOrderQuery) -> Payment:
        payment = await self._repo.find_by_order_id(query.order_id)
        if payment is None:
            raise PaymentNotFoundError(f"No payment found for order '{query.order_id}'")
        return payment
