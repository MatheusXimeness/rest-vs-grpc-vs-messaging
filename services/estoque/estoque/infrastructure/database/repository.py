from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from estoque.application.ports.outbound import IStockRepository
from estoque.domain.stock import Stock
from estoque.infrastructure.database.models import StockModel


class PostgresStockRepository(IStockRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def find_by_product_id(self, product_id: str) -> Stock | None:
        result = await self._session.execute(
            select(StockModel).where(StockModel.product_id == product_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def save(self, stock: Stock) -> None:
        result = await self._session.execute(
            select(StockModel).where(StockModel.product_id == stock.product_id)
        )
        model = result.scalar_one_or_none()
        if model:
            model.quantity_available = stock.quantity_available
            model.quantity_reserved = stock.quantity_reserved
        else:
            self._session.add(StockModel(
                product_id=stock.product_id,
                product_name=stock.product_name,
                quantity_available=stock.quantity_available,
                quantity_reserved=stock.quantity_reserved,
            ))
        await self._session.commit()

    async def find_all(self) -> list[Stock]:
        result = await self._session.execute(select(StockModel))
        return [self._to_domain(m) for m in result.scalars().all()]

    @staticmethod
    def _to_domain(model: StockModel) -> Stock:
        return Stock(
            product_id=model.product_id,
            product_name=model.product_name,
            quantity_available=model.quantity_available,
            quantity_reserved=model.quantity_reserved,
        )
