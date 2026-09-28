from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from pagamento.application.ports.outbound import IPaymentRepository


@asynccontextmanager
async def repository_scope(state) -> AsyncIterator[IPaymentRepository]:
    """Repositório para uma chamada recebida fora do HTTP (gRPC ou mensageria).

    Equivale à injeção de dependências do FastAPI: em memória, reusa o repositório
    único; no postgres, abre uma sessão por chamada.
    """
    if state.session_factory is None:
        yield state.payment_repo
        return
    from pagamento.infrastructure.database.repository import PostgresPaymentRepository
    async with state.session_factory() as session:
        yield PostgresPaymentRepository(session)
