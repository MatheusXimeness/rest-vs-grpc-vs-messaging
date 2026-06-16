from __future__ import annotations

from abc import ABC, abstractmethod

from estoque.domain.stock import Stock


class IStockRepository(ABC):
    @abstractmethod
    async def find_by_product_id(self, product_id: str) -> Stock | None: ...

    @abstractmethod
    async def save(self, stock: Stock) -> None: ...

    @abstractmethod
    async def find_all(self) -> list[Stock]: ...
