"""Handlers das filas do serviço de pagamento (contrato em communication/messaging/rabbitmq)."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from pagamento.application.ports.inbound import ProcessPaymentCommand
from pagamento.application.use_cases.process_payment import ProcessPaymentUseCase
from pagamento.infrastructure.amqp.rpc_server import start_rpc_server
from pagamento.infrastructure.database.session_scope import repository_scope


def _handlers(state) -> dict:
    async def process(payload: dict) -> dict:
        settings = state.settings
        async with repository_scope(state) as repo:
            payment = await ProcessPaymentUseCase(
                repo=repo,
                max_amount=settings.MAX_PAYMENT_AMOUNT,
                decline_rate=settings.DECLINE_RATE,
                rng=state.rng,
            ).execute(
                ProcessPaymentCommand(
                    order_id=UUID(payload["order_id"]),
                    user_id=payload["user_id"],
                    amount=Decimal(payload["amount"]),
                )
            )
        return {
            "status": 200,
            "id": str(payment.id),
            "order_id": str(payment.order_id),
            "approved": payment.approved,
            "transaction_id": payment.transaction_id,
            "decline_reason": payment.decline_reason,
        }

    return {"pagamento.process": process}


async def start_consumer(state, url: str, prefetch: int):
    return await start_rpc_server(url, _handlers(state), prefetch)
