from __future__ import annotations

from pedidos.application.ports.inbound import CreateOrderCommand, ICreateOrderUseCase
from pedidos.application.ports.outbound import (
    IOrderRepository,
    IPaymentServicePort,
    IStockServicePort,
    IUserServicePort,
)
from pedidos.domain.exceptions import InsufficientStockError, PaymentFailedError, UserNotFoundError
from pedidos.domain.order import Order, OrderItem


class CreateOrderUseCase(ICreateOrderUseCase):
    def __init__(
        self,
        order_repo: IOrderRepository,
        user_service: IUserServicePort,
        stock_service: IStockServicePort,
        payment_service: IPaymentServicePort,
    ) -> None:
        self._order_repo = order_repo
        self._user_service = user_service
        self._stock_service = stock_service
        self._payment_service = payment_service

    async def execute(self, command: CreateOrderCommand) -> Order:
        await self._user_service.get_user(command.user_id)

        items = [
            OrderItem(
                product_id=i.product_id,
                quantity=i.quantity,
                unit_price=i.unit_price,
            )
            for i in command.items
        ]

        reserved: list[OrderItem] = []
        try:
            for item in items:
                reservation = await self._stock_service.reserve_stock(
                    item.product_id, item.quantity
                )
                if not reservation.reserved:
                    raise InsufficientStockError(
                        f"Insufficient stock for product '{item.product_id}'"
                    )
                reserved.append(item)
        except InsufficientStockError:
            for item in reserved:
                await self._stock_service.release_stock(item.product_id, item.quantity)
            raise

        order = Order.create(user_id=command.user_id, items=items)

        payment = await self._payment_service.process_payment(
            order_id=order.id,
            amount=order.total,
            user_id=command.user_id,
        )
        if not payment.approved:
            for item in items:
                await self._stock_service.release_stock(item.product_id, item.quantity)
            raise PaymentFailedError("Payment was not approved")

        order.confirm()
        await self._order_repo.save(order)
        return order
