from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from pagamento.domain.payment import Payment


@dataclass
class ProcessPaymentCommand:
    order_id: UUID
    user_id: str
    amount: Decimal


@dataclass
class GetPaymentQuery:
    payment_id: UUID


@dataclass
class GetPaymentByOrderQuery:
    order_id: UUID


class IProcessPaymentUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ProcessPaymentCommand) -> Payment: ...


class IGetPaymentUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetPaymentQuery) -> Payment: ...


class IGetPaymentByOrderUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetPaymentByOrderQuery) -> Payment: ...
