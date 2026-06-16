from __future__ import annotations

from uuid import UUID

from pedidos.application.ports.outbound import IOrderRepository
from pedidos.domain.order import Order


class InMemoryOrderRepository(IOrderRepository):
    """Repositório em memória — usado para testes sem banco de dados real."""

    def __init__(self) -> None:
        self._store: dict[UUID, Order] = {}

    async def save(self, order: Order) -> None:
        self._store[order.id] = order

    async def find_by_id(self, order_id: UUID) -> Order | None:
        return self._store.get(order_id)

    async def find_by_user(self, user_id: str) -> list[Order]:
        return [o for o in self._store.values() if o.user_id == user_id]

    async def find_all(self) -> list[Order]:
        return list(self._store.values())
