from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from pedidos.domain.order import Order


@dataclass
class UserInfo:
    id: str
    name: str
    email: str


@dataclass
class StockReservation:
    product_id: str
    quantity: int
    reserved: bool


@dataclass
class PaymentResult:
    order_id: UUID
    approved: bool
    transaction_id: str | None


class IOrderRepository(ABC):
    @abstractmethod
    async def save(self, order: Order) -> None: ...

    @abstractmethod
    async def find_by_id(self, order_id: UUID) -> Order | None: ...

    @abstractmethod
    async def find_by_user(self, user_id: str) -> list[Order]: ...

    @abstractmethod
    async def find_all(self) -> list[Order]: ...


class IUserServicePort(ABC):
    @abstractmethod
    async def get_user(self, user_id: str) -> UserInfo: ...


class IStockServicePort(ABC):
    @abstractmethod
    async def reserve_stock(self, product_id: str, quantity: int) -> StockReservation: ...

    @abstractmethod
    async def release_stock(self, product_id: str, quantity: int) -> None: ...


class IPaymentServicePort(ABC):
    @abstractmethod
    async def process_payment(
        self, order_id: UUID, amount: Decimal, user_id: str
    ) -> PaymentResult: ...
