from __future__ import annotations

from estoque.application.ports.inbound import GetStockQuery, IGetStockUseCase, IListStockUseCase
from estoque.application.ports.outbound import IStockRepository
from estoque.domain.exceptions import ProductNotFoundError
from estoque.domain.stock import Stock


class GetStockUseCase(IGetStockUseCase):
    def __init__(self, repo: IStockRepository) -> None:
        self._repo = repo

    async def execute(self, query: GetStockQuery) -> Stock:
        stock = await self._repo.find_by_product_id(query.product_id)
        if stock is None:
            raise ProductNotFoundError(f"Product '{query.product_id}' not found")
        return stock


class ListStockUseCase(IListStockUseCase):
    def __init__(self, repo: IStockRepository) -> None:
        self._repo = repo

    async def execute(self) -> list[Stock]:
        return await self._repo.find_all()
