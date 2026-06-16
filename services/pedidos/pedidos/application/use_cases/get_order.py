from __future__ import annotations

from pedidos.application.ports.inbound import (
    GetOrderQuery,
    IGetOrderUseCase,
    IListOrdersUseCase,
    ListOrdersQuery,
)
from pedidos.application.ports.outbound import IOrderRepository
from pedidos.domain.exceptions import OrderNotFoundError
from pedidos.domain.order import Order


class GetOrderUseCase(IGetOrderUseCase):
    def __init__(self, order_repo: IOrderRepository) -> None:
        self._order_repo = order_repo

    async def execute(self, query: GetOrderQuery) -> Order:
        order = await self._order_repo.find_by_id(query.order_id)
        if order is None:
            raise OrderNotFoundError(f"Order '{query.order_id}' not found")
        return order


class ListOrdersUseCase(IListOrdersUseCase):
    def __init__(self, order_repo: IOrderRepository) -> None:
        self._order_repo = order_repo

    async def execute(self, query: ListOrdersQuery) -> list[Order]:
        if query.user_id:
            return await self._order_repo.find_by_user(query.user_id)
        return await self._order_repo.find_all()
