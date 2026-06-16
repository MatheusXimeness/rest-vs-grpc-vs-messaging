from decimal import Decimal
from uuid import UUID

import httpx

from pedidos.application.ports.outbound import IPaymentServicePort, PaymentResult
from pedidos.domain.exceptions import PaymentFailedError


class PaymentHttpClient(IPaymentServicePort):
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self._base_url = base_url.rstrip("/")
        self._client = client

    async def process_payment(
        self, order_id: UUID, amount: Decimal, user_id: str
    ) -> PaymentResult:
        try:
            response = await self._client.post(
                f"{self._base_url}/payments",
                json={
                    "order_id": str(order_id),
                    "amount": str(amount),
                    "user_id": user_id,
                },
            )
        except httpx.RequestError as exc:
            raise PaymentFailedError(f"Pagamento service unavailable: {exc}") from exc

        if response.status_code in (402, 422):
            raise PaymentFailedError("Payment was declined")

        response.raise_for_status()
        data = response.json()
        return PaymentResult(
            order_id=UUID(data["order_id"]),
            approved=data["approved"],
            transaction_id=data.get("transaction_id"),
        )
