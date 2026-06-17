from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4


class PaymentStatus(str, Enum):
    APPROVED = "approved"
    DECLINED = "declined"


@dataclass
class Payment:
    id: UUID
    order_id: UUID
    user_id: str
    amount: Decimal
    status: PaymentStatus
    transaction_id: str | None
    created_at: datetime
    decline_reason: str | None = None

    @property
    def approved(self) -> bool:
        return self.status == PaymentStatus.APPROVED

    @classmethod
    def approve(cls, order_id: UUID, user_id: str, amount: Decimal) -> "Payment":
        return cls(
            id=uuid4(),
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            status=PaymentStatus.APPROVED,
            transaction_id=str(uuid4()),
            created_at=datetime.now(timezone.utc),
        )

    @classmethod
    def decline(cls, order_id: UUID, user_id: str, amount: Decimal, reason: str) -> "Payment":
        return cls(
            id=uuid4(),
            order_id=order_id,
            user_id=user_id,
            amount=amount,
            status=PaymentStatus.DECLINED,
            transaction_id=None,
            created_at=datetime.now(timezone.utc),
            decline_reason=reason,
        )
