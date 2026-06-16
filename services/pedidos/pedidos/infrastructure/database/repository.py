from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from pedidos.application.ports.outbound import IOrderRepository
from pedidos.domain.order import Order, OrderItem, OrderStatus
from pedidos.infrastructure.database.models import OrderItemModel, OrderModel


class PostgresOrderRepository(IOrderRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, order: Order) -> None:
        model = OrderModel(
            id=order.id,
            user_id=order.user_id,
            status=order.status.value,
            total=order.total,
            created_at=order.created_at,
            items=[
                OrderItemModel(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price,
                )
                for item in order.items
            ],
        )
        self._session.add(model)
        await self._session.commit()

    async def find_by_id(self, order_id: UUID) -> Order | None:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_user(self, user_id: str) -> list[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .where(OrderModel.user_id == user_id)
            .order_by(OrderModel.created_at.desc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    async def find_all(self) -> list[Order]:
        result = await self._session.execute(
            select(OrderModel)
            .options(selectinload(OrderModel.items))
            .order_by(OrderModel.created_at.desc())
        )
        return [self._to_domain(m) for m in result.scalars().all()]

    @staticmethod
    def _to_domain(model: OrderModel) -> Order:
        return Order(
            id=model.id,
            user_id=model.user_id,
            items=[
                OrderItem(
                    product_id=item.product_id,
                    quantity=item.quantity,
                    unit_price=Decimal(str(item.unit_price)),
                )
                for item in model.items
            ],
            status=OrderStatus(model.status),
            total=Decimal(str(model.total)),
            created_at=model.created_at,
        )
