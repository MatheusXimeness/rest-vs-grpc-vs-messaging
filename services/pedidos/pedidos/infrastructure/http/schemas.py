from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator


class OrderItemRequest(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be greater than zero")
        return v

    @field_validator("unit_price")
    @classmethod
    def price_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("unit_price must be greater than zero")
        return v


class CreateOrderRequest(BaseModel):
    user_id: str
    items: list[OrderItemRequest]

    @field_validator("items")
    @classmethod
    def items_must_not_be_empty(cls, v: list) -> list:
        if not v:
            raise ValueError("order must have at least one item")
        return v


class OrderItemResponse(BaseModel):
    product_id: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class OrderResponse(BaseModel):
    id: UUID
    user_id: str
    items: list[OrderItemResponse]
    status: str
    total: Decimal
    created_at: datetime
