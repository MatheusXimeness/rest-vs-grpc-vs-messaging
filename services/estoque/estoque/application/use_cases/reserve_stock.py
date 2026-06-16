from __future__ import annotations

from estoque.application.ports.inbound import IReserveStockUseCase, ReserveStockCommand
from estoque.application.ports.outbound import IStockRepository
from estoque.domain.exceptions import ProductNotFoundError
from estoque.domain.stock import Stock


class ReserveStockUseCase(IReserveStockUseCase):
    def __init__(self, repo: IStockRepository) -> None:
        self._repo = repo

    async def execute(self, command: ReserveStockCommand) -> Stock:
        stock = await self._repo.find_by_product_id(command.product_id)
        if stock is None:
            raise ProductNotFoundError(f"Product '{command.product_id}' not found")
        stock.reserve(command.quantity)
        await self._repo.save(stock)
        return stock
