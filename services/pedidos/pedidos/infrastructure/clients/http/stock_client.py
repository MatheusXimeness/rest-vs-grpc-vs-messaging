import httpx

from pedidos.application.ports.outbound import IStockServicePort, StockReservation
from pedidos.domain.exceptions import InsufficientStockError


class StockHttpClient(IStockServicePort):
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def reserve_stock(self, product_id: str, quantity: int) -> StockReservation:
        try:
            response = await self._client.post(
                f"{self._base_url}/stock/reserve",
                json={"product_id": product_id, "quantity": quantity},
            )
        except httpx.RequestError as exc:
            raise InsufficientStockError(f"Estoque service unavailable: {exc}") from exc

        if response.status_code == 404:
            raise InsufficientStockError(
                f"Product '{product_id}' not found in stock"
            )

        if response.status_code == 422:
            raise InsufficientStockError(
                f"Insufficient stock for product '{product_id}'"
            )

        response.raise_for_status()
        data = response.json()
        return StockReservation(
            product_id=data["product_id"],
            quantity=data["quantity"],
            reserved=data["reserved"],
        )

    async def release_stock(self, product_id: str, quantity: int) -> None:
        try:
            await self._client.post(
                f"{self._base_url}/stock/release",
                json={"product_id": product_id, "quantity": quantity},
            )
        except httpx.RequestError:
            pass
