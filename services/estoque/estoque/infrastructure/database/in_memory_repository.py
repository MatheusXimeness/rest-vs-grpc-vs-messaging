from __future__ import annotations

import copy

from estoque.application.ports.outbound import IStockRepository
from estoque.domain.stock import Stock

_INITIAL_STOCK: dict[str, Stock] = {
    "mouse": Stock(product_id="mouse", product_name="Mouse USB", quantity_available=100),
    "keyboard": Stock(product_id="keyboard", product_name="Teclado Mecânico", quantity_available=50),
    "monitor": Stock(product_id="monitor", product_name='Monitor 24"', quantity_available=20),
    "headset": Stock(product_id="headset", product_name="Headset Gamer", quantity_available=75),
    "webcam": Stock(product_id="webcam", product_name="Webcam HD", quantity_available=30),
}


class InMemoryStockRepository(IStockRepository):
    def __init__(self) -> None:
        self._store: dict[str, Stock] = copy.deepcopy(_INITIAL_STOCK)

    async def find_by_product_id(self, product_id: str) -> Stock | None:
        return self._store.get(product_id)

    async def save(self, stock: Stock) -> None:
        self._store[stock.product_id] = stock

    async def find_all(self) -> list[Stock]:
        return list(self._store.values())
