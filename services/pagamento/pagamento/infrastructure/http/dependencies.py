from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from pagamento.application.ports.outbound import IPaymentRepository
from pagamento.application.use_cases.get_payment import GetPaymentByOrderUseCase, GetPaymentUseCase
from pagamento.application.use_cases.process_payment import ProcessPaymentUseCase


async def _get_db(request: Request) -> AsyncGenerator[AsyncSession | None, None]:
    if request.app.state.session_factory is None:
        yield None
        return
    async with request.app.state.session_factory() as session:
        yield session


def get_payment_repo(request: Request, session: AsyncSession = Depends(_get_db)) -> IPaymentRepository:
    if request.app.state.settings.USE_IN_MEMORY_DB:
        return request.app.state.payment_repo
    from pagamento.infrastructure.database.repository import PostgresPaymentRepository
    return PostgresPaymentRepository(session)


def get_process_payment_use_case(
    request: Request,
    repo: IPaymentRepository = Depends(get_payment_repo),
) -> ProcessPaymentUseCase:
    return ProcessPaymentUseCase(
        repo=repo,
        max_amount=request.app.state.settings.MAX_PAYMENT_AMOUNT,
        decline_rate=request.app.state.settings.DECLINE_RATE,
    )


def get_get_payment_use_case(repo: IPaymentRepository = Depends(get_payment_repo)) -> GetPaymentUseCase:
    return GetPaymentUseCase(repo)


def get_get_payment_by_order_use_case(repo: IPaymentRepository = Depends(get_payment_repo)) -> GetPaymentByOrderUseCase:
    return GetPaymentByOrderUseCase(repo)
