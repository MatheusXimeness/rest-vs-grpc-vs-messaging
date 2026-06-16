from __future__ import annotations

from dataclasses import dataclass

from estoque.domain.exceptions import InsufficientStockError


@dataclass
class Stock:
    product_id: str
    product_name: str
    quantity_available: int
    quantity_reserved: int = 0

    def reserve(self, quantity: int) -> None:
        if quantity > self.quantity_available:
            raise InsufficientStockError(
                f"Insufficient stock for '{self.product_id}': "
                f"requested {quantity}, available {self.quantity_available}"
            )
        self.quantity_available -= quantity
        self.quantity_reserved += quantity

    def release(self, quantity: int) -> None:
        qty = min(quantity, self.quantity_reserved)
        self.quantity_reserved -= qty
        self.quantity_available += qty
