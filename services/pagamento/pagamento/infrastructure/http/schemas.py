from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator


class ProcessPaymentRequest(BaseModel):
    order_id: UUID
    user_id: str
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("amount must be greater than zero")
        return v


class PaymentResponse(BaseModel):
    id: UUID
    order_id: UUID
    user_id: str
    amount: Decimal
    status: str
    approved: bool
    transaction_id: str | None
    decline_reason: str | None
    created_at: datetime
