import asyncio

import aiohttp

from pedidos.application.ports.outbound import IStockServicePort, StockReservation
from pedidos.domain.exceptions import DependencyUnavailableError, InsufficientStockError


class StockHttpClient(IStockServicePort):
    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session

    async def reserve_stock(self, product_id: str, quantity: int) -> StockReservation:
        try:
            async with self._session.post(
                f"{self._base_url}/stock/reserve",
                json={"product_id": product_id, "quantity": quantity},
            ) as response:
                if response.status == 404:
                    raise InsufficientStockError(
                        f"Product '{product_id}' not found in stock"
                    )
                if response.status == 422:
                    raise InsufficientStockError(
                        f"Insufficient stock for product '{product_id}'"
                    )
                response.raise_for_status()
                data = await response.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as exc:
            raise DependencyUnavailableError(f"Estoque service unavailable: {exc!r}") from exc

        return StockReservation(
            product_id=data["product_id"],
            quantity=data["quantity"],
            reserved=data["reserved"],
        )

    async def release_stock(self, product_id: str, quantity: int) -> None:
        try:
            async with self._session.post(
                f"{self._base_url}/stock/release",
                json={"product_id": product_id, "quantity": quantity},
            ):
                pass
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass
