from __future__ import annotations

from pedidos.application.ports.outbound import IStockServicePort, StockReservation


class StockStubAdapter(IStockServicePort):
    async def reserve_stock(self, product_id: str, quantity: int) -> StockReservation:
        return StockReservation(product_id=product_id, quantity=quantity, reserved=True)

    async def release_stock(self, product_id: str, quantity: int) -> None:
        pass
