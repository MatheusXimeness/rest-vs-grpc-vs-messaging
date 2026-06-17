from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pagamento.application.ports.outbound import IPaymentRepository
from pagamento.domain.payment import Payment, PaymentStatus
from pagamento.infrastructure.database.models import PaymentModel


class PostgresPaymentRepository(IPaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, payment: Payment) -> None:
        model = PaymentModel(
            id=payment.id,
            order_id=payment.order_id,
            user_id=payment.user_id,
            amount=payment.amount,
            status=payment.status.value,
            transaction_id=payment.transaction_id,
            decline_reason=payment.decline_reason,
            created_at=payment.created_at,
        )
        self._session.add(model)
        await self._session.commit()

    async def find_by_id(self, payment_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.id == payment_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_order_id(self, order_id: UUID) -> Payment | None:
        result = await self._session.execute(
            select(PaymentModel).where(PaymentModel.order_id == order_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    @staticmethod
    def _to_domain(model: PaymentModel) -> Payment:
        return Payment(
            id=model.id,
            order_id=model.order_id,
            user_id=model.user_id,
            amount=Decimal(str(model.amount)),
            status=PaymentStatus(model.status),
            transaction_id=model.transaction_id,
            decline_reason=model.decline_reason,
            created_at=model.created_at,
        )
