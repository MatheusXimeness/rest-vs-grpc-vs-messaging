from __future__ import annotations

import random
from decimal import Decimal

from pagamento.application.ports.inbound import IProcessPaymentUseCase, ProcessPaymentCommand
from pagamento.application.ports.outbound import IPaymentRepository
from pagamento.domain.payment import Payment


class ProcessPaymentUseCase(IProcessPaymentUseCase):
    def __init__(
        self,
        repo: IPaymentRepository,
        max_amount: Decimal,
        decline_rate: float,
    ) -> None:
        self._repo = repo
        self._max_amount = max_amount
        self._decline_rate = decline_rate

    async def execute(self, command: ProcessPaymentCommand) -> Payment:
        if command.amount > self._max_amount:
            payment = Payment.decline(
                order_id=command.order_id,
                user_id=command.user_id,
                amount=command.amount,
                reason=f"Amount {command.amount} exceeds limit of {self._max_amount}",
            )
        elif random.random() < self._decline_rate:
            payment = Payment.decline(
                order_id=command.order_id,
                user_id=command.user_id,
                amount=command.amount,
                reason="Payment declined by issuer",
            )
        else:
            payment = Payment.approve(
                order_id=command.order_id,
                user_id=command.user_id,
                amount=command.amount,
            )

        await self._repo.save(payment)
        return payment
