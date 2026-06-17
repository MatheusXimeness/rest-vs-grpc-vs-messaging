from __future__ import annotations

from uuid import UUID

from pagamento.application.ports.outbound import IPaymentRepository
from pagamento.domain.payment import Payment


class InMemoryPaymentRepository(IPaymentRepository):
    def __init__(self) -> None:
        self._store: dict[UUID, Payment] = {}

    async def save(self, payment: Payment) -> None:
        self._store[payment.id] = payment

    async def find_by_id(self, payment_id: UUID) -> Payment | None:
        return self._store.get(payment_id)

    async def find_by_order_id(self, order_id: UUID) -> Payment | None:
        return next((p for p in self._store.values() if p.order_id == order_id), None)
