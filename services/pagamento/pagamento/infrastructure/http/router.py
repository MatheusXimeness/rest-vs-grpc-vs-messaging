from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from pagamento.application.ports.inbound import (
    GetPaymentByOrderQuery,
    GetPaymentQuery,
    ProcessPaymentCommand,
)
from pagamento.application.use_cases.get_payment import GetPaymentByOrderUseCase, GetPaymentUseCase
from pagamento.application.use_cases.process_payment import ProcessPaymentUseCase
from pagamento.domain.exceptions import PaymentNotFoundError
from pagamento.domain.payment import Payment
from pagamento.infrastructure.http.dependencies import (
    get_get_payment_by_order_use_case,
    get_get_payment_use_case,
    get_process_payment_use_case,
)
from pagamento.infrastructure.http.schemas import PaymentResponse, ProcessPaymentRequest

router = APIRouter(prefix="/payments", tags=["payments"])


def _to_response(payment: Payment) -> PaymentResponse:
    return PaymentResponse(
        id=payment.id,
        order_id=payment.order_id,
        user_id=payment.user_id,
        amount=payment.amount,
        status=payment.status.value,
        approved=payment.approved,
        transaction_id=payment.transaction_id,
        decline_reason=payment.decline_reason,
        created_at=payment.created_at,
    )


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def process_payment(
    body: ProcessPaymentRequest,
    use_case: ProcessPaymentUseCase = Depends(get_process_payment_use_case),
) -> PaymentResponse:
    payment = await use_case.execute(ProcessPaymentCommand(
        order_id=body.order_id,
        user_id=body.user_id,
        amount=body.amount,
    ))
    return _to_response(payment)


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: UUID,
    use_case: GetPaymentByOrderUseCase = Depends(get_get_payment_by_order_use_case),
) -> PaymentResponse:
    try:
        payment = await use_case.execute(GetPaymentByOrderQuery(order_id=order_id))
        return _to_response(payment)
    except PaymentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: UUID,
    use_case: GetPaymentUseCase = Depends(get_get_payment_use_case),
) -> PaymentResponse:
    try:
        payment = await use_case.execute(GetPaymentQuery(payment_id=payment_id))
        return _to_response(payment)
    except PaymentNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
