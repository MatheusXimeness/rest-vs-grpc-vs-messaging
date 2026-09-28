import asyncio
from decimal import Decimal
from uuid import UUID

import aiohttp

from pedidos.application.ports.outbound import IPaymentServicePort, PaymentResult
from pedidos.domain.exceptions import DependencyUnavailableError, PaymentFailedError


class PaymentHttpClient(IPaymentServicePort):
    def __init__(self, base_url: str, session: aiohttp.ClientSession) -> None:
        self._base_url = base_url.rstrip("/")
        self._session = session

    async def process_payment(
        self, order_id: UUID, amount: Decimal, user_id: str
    ) -> PaymentResult:
        try:
            async with self._session.post(
                f"{self._base_url}/payments",
                json={
                    "order_id": str(order_id),
                    "amount": str(amount),
                    "user_id": user_id,
                },
            ) as response:
                if response.status in (402, 422):
                    raise PaymentFailedError("Payment was declined")
                response.raise_for_status()
                data = await response.json()
        except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as exc:
            raise DependencyUnavailableError(f"Pagamento service unavailable: {exc!r}") from exc

        return PaymentResult(
            order_id=UUID(data["order_id"]),
            approved=data["approved"],
            transaction_id=data.get("transaction_id"),
        )
