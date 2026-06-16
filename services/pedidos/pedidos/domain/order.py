from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pedidos.domain.exceptions import InvalidOrderStateError


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


@dataclass
class OrderItem:
    product_id: str
    quantity: int
    unit_price: Decimal

    @property
    def subtotal(self) -> Decimal:
        return self.unit_price * self.quantity


@dataclass
class Order:
    id: UUID
    user_id: str
    items: list[OrderItem]
    status: OrderStatus
    total: Decimal
    created_at: datetime

    @classmethod
    def create(cls, user_id: str, items: list[OrderItem]) -> "Order":
        total = sum(item.subtotal for item in items)
        return cls(
            id=uuid4(),
            user_id=user_id,
            items=list(items),
            status=OrderStatus.PENDING,
            total=total,
            created_at=datetime.now(timezone.utc),
        )

    def confirm(self) -> None:
        if self.status != OrderStatus.PENDING:
            raise InvalidOrderStateError(
                f"Cannot confirm order with status '{self.status}'"
            )
        self.status = OrderStatus.CONFIRMED

    def cancel(self) -> None:
        if self.status == OrderStatus.CONFIRMED:
            raise InvalidOrderStateError("Cannot cancel a confirmed order")
        self.status = OrderStatus.CANCELLED
