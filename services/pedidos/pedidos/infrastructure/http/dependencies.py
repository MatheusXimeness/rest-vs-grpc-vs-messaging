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


# Cada porta de saída tem um adaptador por estratégia de comunicação (http, grpc, amqp).
# O caso de uso recebe só a interface, então a troca de estratégia não altera o domínio.


def _user_service(request: Request) -> IUserServicePort:
    state = request.app.state
    if state.settings.USE_STUB_SERVICES:
        from pedidos.infrastructure.clients.stubs.user_stub import UserStubAdapter
        return UserStubAdapter()
    if state.settings.COMMUNICATION_STRATEGY == "grpc":
        from pedidos.infrastructure.clients.grpc.user_client import UserGrpcClient
        return UserGrpcClient(state.grpc_stubs.user, state.settings.REQUEST_TIMEOUT_S)
    if state.settings.COMMUNICATION_STRATEGY == "mensageria":
        from pedidos.infrastructure.clients.amqp.user_client import UserAmqpClient
        return UserAmqpClient(state.amqp_rpc)
    from pedidos.infrastructure.clients.http.user_client import UserHttpClient
    return UserHttpClient(
        request.app.state.settings.USUARIO_SERVICE_URL,
        request.app.state.http_client,
    )


def _stock_service(request: Request) -> IStockServicePort:
    state = request.app.state
    if state.settings.USE_STUB_STOCK:
        from pedidos.infrastructure.clients.stubs.stock_stub import StockStubAdapter
        return StockStubAdapter()
    if state.settings.COMMUNICATION_STRATEGY == "grpc":
        from pedidos.infrastructure.clients.grpc.stock_client import StockGrpcClient
        return StockGrpcClient(state.grpc_stubs.stock, state.settings.REQUEST_TIMEOUT_S)
    if state.settings.COMMUNICATION_STRATEGY == "mensageria":
        from pedidos.infrastructure.clients.amqp.stock_client import StockAmqpClient
        return StockAmqpClient(state.amqp_rpc)
    from pedidos.infrastructure.clients.http.stock_client import StockHttpClient
    return StockHttpClient(
        request.app.state.settings.ESTOQUE_SERVICE_URL,
        request.app.state.http_client,
    )


def _payment_service(request: Request) -> IPaymentServicePort:
    state = request.app.state
    if state.settings.USE_STUB_PAYMENT:
        from pedidos.infrastructure.clients.stubs.payment_stub import PaymentStubAdapter
        return PaymentStubAdapter()
    if state.settings.COMMUNICATION_STRATEGY == "grpc":
        from pedidos.infrastructure.clients.grpc.payment_client import PaymentGrpcClient
        return PaymentGrpcClient(state.grpc_stubs.payment, state.settings.REQUEST_TIMEOUT_S)
    if state.settings.COMMUNICATION_STRATEGY == "mensageria":
        from pedidos.infrastructure.clients.amqp.payment_client import PaymentAmqpClient
        return PaymentAmqpClient(state.amqp_rpc)
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
