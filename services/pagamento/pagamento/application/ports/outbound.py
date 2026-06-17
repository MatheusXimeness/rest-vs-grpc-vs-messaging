from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from pagamento.domain.payment import Payment


class IPaymentRepository(ABC):
    @abstractmethod
    async def save(self, payment: Payment) -> None: ...

    @abstractmethod
    async def find_by_id(self, payment_id: UUID) -> Payment | None: ...

    @abstractmethod
    async def find_by_order_id(self, order_id: UUID) -> Payment | None: ...
