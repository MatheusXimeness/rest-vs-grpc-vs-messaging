from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from pedidos.application.ports.outbound import (
    IOrderRepository,
    IPaymentServicePort,
    IStockServicePort,
    IUserServicePort,
)
from pedidos.application.use_cases.create_order import CreateOrderUseCase
from pedidos.application.use_cases.get_order import GetOrderUseCase, ListOrdersUseCase


async def _get_db(request: Request) -> AsyncGenerator[AsyncSession | None, None]:
    if request.app.state.session_factory is None:
        yield None
        return
    async with request.app.state.session_factory() as session:
        yield session


def get_order_repo(request: Request, session: AsyncSession = Depends(_get_db)) -> IOrderRepository:
    if request.app.state.settings.USE_IN_MEMORY_DB:
        return request.app.state.order_repo
    from pedidos.infrastructure.database.repository import PostgresOrderRepository
    return PostgresOrderRepository(session)


def _user_service(request: Request) -> IUserServicePort:
    if request.app.state.settings.USE_STUB_SERVICES:
        from pedidos.infrastructure.clients.stubs.user_stub import UserStubAdapter
        return UserStubAdapter()
    from pedidos.infrastructure.clients.http.user_client import UserHttpClient
    return UserHttpClient(
        request.app.state.settings.USUARIO_SERVICE_URL,
        request.app.state.http_client,
    )


def _stock_service(request: Request) -> IStockServicePort:
    if request.app.state.settings.USE_STUB_STOCK:
        from pedidos.infrastructure.clients.stubs.stock_stub import StockStubAdapter
        return StockStubAdapter()
    from pedidos.infrastructure.clients.http.stock_client import StockHttpClient
    return StockHttpClient(
        request.app.state.settings.ESTOQUE_SERVICE_URL,
        request.app.state.http_client,
    )


def _payment_service(request: Request) -> IPaymentServicePort:
    if request.app.state.settings.USE_STUB_PAYMENT:
        from pedidos.infrastructure.clients.stubs.payment_stub import PaymentStubAdapter
        return PaymentStubAdapter()
    from pedidos.infrastructure.clients.http.payment_client import PaymentHttpClient
    return PaymentHttpClient(
        request.app.state.settings.PAGAMENTO_SERVICE_URL,
        request.app.state.http_client,
    )


def get_create_order_use_case(
    request: Request,
    order_repo: IOrderRepository = Depends(get_order_repo),
) -> CreateOrderUseCase:
    return CreateOrderUseCase(
        order_repo=order_repo,
        user_service=_user_service(request),
        stock_service=_stock_service(request),
        payment_service=_payment_service(request),
    )


def get_get_order_use_case(
    order_repo: IOrderRepository = Depends(get_order_repo),
) -> GetOrderUseCase:
    return GetOrderUseCase(order_repo)


def get_list_orders_use_case(
    order_repo: IOrderRepository = Depends(get_order_repo),
) -> ListOrdersUseCase:
    return ListOrdersUseCase(order_repo)
