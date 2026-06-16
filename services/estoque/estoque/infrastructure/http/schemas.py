from pydantic import BaseModel, field_validator


class StockOperationRequest(BaseModel):
    product_id: str
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("quantity must be greater than zero")
        return v


class ReserveStockResponse(BaseModel):
    product_id: str
    quantity: int
    reserved: bool


class StockResponse(BaseModel):
    product_id: str
    product_name: str
    quantity_available: int
    quantity_reserved: int
