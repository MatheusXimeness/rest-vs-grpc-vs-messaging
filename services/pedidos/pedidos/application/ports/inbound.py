from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from pedidos.domain.order import Order


@dataclass
class CreateOrderItemCommand:
    product_id: str
    quantity: int
    unit_price: Decimal


@dataclass
class CreateOrderCommand:
    user_id: str
    items: list[CreateOrderItemCommand]


@dataclass
class GetOrderQuery:
    order_id: UUID


@dataclass
class ListOrdersQuery:
    user_id: str | None = None


class ICreateOrderUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateOrderCommand) -> Order: ...


class IGetOrderUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetOrderQuery) -> Order: ...


class IListOrdersUseCase(ABC):
    @abstractmethod
    async def execute(self, query: ListOrdersQuery) -> list[Order]: ...
