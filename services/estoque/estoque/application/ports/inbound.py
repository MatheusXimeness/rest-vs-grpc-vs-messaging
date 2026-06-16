from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from estoque.domain.stock import Stock


@dataclass
class ReserveStockCommand:
    product_id: str
    quantity: int


@dataclass
class ReleaseStockCommand:
    product_id: str
    quantity: int


@dataclass
class GetStockQuery:
    product_id: str


class IReserveStockUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ReserveStockCommand) -> Stock: ...


class IReleaseStockUseCase(ABC):
    @abstractmethod
    async def execute(self, command: ReleaseStockCommand) -> None: ...


class IGetStockUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetStockQuery) -> Stock: ...


class IListStockUseCase(ABC):
    @abstractmethod
    async def execute(self) -> list[Stock]: ...
