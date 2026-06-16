from __future__ import annotations

from estoque.application.ports.inbound import IReleaseStockUseCase, ReleaseStockCommand
from estoque.application.ports.outbound import IStockRepository
from estoque.domain.exceptions import ProductNotFoundError


class ReleaseStockUseCase(IReleaseStockUseCase):
    def __init__(self, repo: IStockRepository) -> None:
        self._repo = repo

    async def execute(self, command: ReleaseStockCommand) -> None:
        stock = await self._repo.find_by_product_id(command.product_id)
        if stock is None:
            raise ProductNotFoundError(f"Product '{command.product_id}' not found")
        stock.release(command.quantity)
        await self._repo.save(stock)
