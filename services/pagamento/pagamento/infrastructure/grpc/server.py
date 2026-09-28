"""Servidor gRPC: adaptador de entrada da estratégia gRPC (contrato em communication/grpc/proto)."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID

import grpc

import ecommerce_pb2
import ecommerce_pb2_grpc
from pagamento.application.ports.inbound import ProcessPaymentCommand
from pagamento.application.use_cases.process_payment import ProcessPaymentUseCase
from pagamento.infrastructure.database.session_scope import repository_scope
from pagamento.infrastructure.metrics import track


class PaymentServicer(ecommerce_pb2_grpc.PaymentServiceServicer):
    def __init__(self, state) -> None:
        self._state = state

    async def ProcessPayment(self, request, context):
        with track("GRPC", "/ecommerce.PaymentService/ProcessPayment"):
            settings = self._state.settings
            async with repository_scope(self._state) as repo:
                payment = await ProcessPaymentUseCase(
                    repo=repo,
                    max_amount=settings.MAX_PAYMENT_AMOUNT,
                    decline_rate=settings.DECLINE_RATE,
                    rng=self._state.rng,
                ).execute(
                    ProcessPaymentCommand(
                        order_id=UUID(request.order_id),
                        user_id=request.user_id,
                        amount=Decimal(request.amount),
                    )
                )
            return ecommerce_pb2.Payment(
                id=str(payment.id),
                order_id=str(payment.order_id),
                approved=payment.approved,
                transaction_id=payment.transaction_id or "",
                decline_reason=payment.decline_reason or "",
            )


async def start_grpc_server(state, port: int) -> grpc.aio.Server:
    server = grpc.aio.server()
    ecommerce_pb2_grpc.add_PaymentServiceServicer_to_server(PaymentServicer(state), server)
    server.add_insecure_port(f"[::]:{port}")
    await server.start()
    return server
