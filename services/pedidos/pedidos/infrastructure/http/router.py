from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from pedidos.application.ports.inbound import (
    CreateOrderCommand,
    CreateOrderItemCommand,
    GetOrderQuery,
    ListOrdersQuery,
)
from pedidos.application.use_cases.create_order import CreateOrderUseCase
from pedidos.application.use_cases.get_order import GetOrderUseCase, ListOrdersUseCase
from pedidos.domain.exceptions import (
    DependencyUnavailableError,
    InsufficientStockError,
    OrderNotFoundError,
    PaymentFailedError,
    UserNotFoundError,
)
from pedidos.domain.order import Order
from pedidos.infrastructure.http.dependencies import (
    get_create_order_use_case,
    get_get_order_use_case,
    get_list_orders_use_case,
)
from pedidos.infrastructure.http.schemas import (
    CreateOrderRequest,
    OrderItemResponse,
    OrderResponse,
)

router = APIRouter(prefix="/orders", tags=["orders"])


def _to_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        items=[
            OrderItemResponse(
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
                subtotal=item.subtotal,
            )
            for item in order.items
        ],
        status=order.status.value,
        total=order.total,
        created_at=order.created_at,
    )


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    body: CreateOrderRequest,
    use_case: CreateOrderUseCase = Depends(get_create_order_use_case),
) -> OrderResponse:
    try:
        order = await use_case.execute(
            CreateOrderCommand(
                user_id=body.user_id,
                items=[
                    CreateOrderItemCommand(
                        product_id=i.product_id,
                        quantity=i.quantity,
                        unit_price=i.unit_price,
                    )
                    for i in body.items
                ],
            )
        )
        return _to_response(order)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    except PaymentFailedError as exc:
        raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(exc))
    except DependencyUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc))


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: UUID,
    use_case: GetOrderUseCase = Depends(get_get_order_use_case),
) -> OrderResponse:
    try:
        order = await use_case.execute(GetOrderQuery(order_id=order_id))
        return _to_response(order)
    except OrderNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/", response_model=list[OrderResponse])
async def list_orders(
    user_id: str | None = None,
    use_case: ListOrdersUseCase = Depends(get_list_orders_use_case),
) -> list[OrderResponse]:
    orders = await use_case.execute(ListOrdersQuery(user_id=user_id))
    return [_to_response(o) for o in orders]
