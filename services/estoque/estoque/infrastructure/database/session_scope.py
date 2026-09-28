from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from estoque.application.ports.outbound import IStockRepository


@asynccontextmanager
async def repository_scope(state) -> AsyncIterator[IStockRepository]:
    """Repositório para uma chamada recebida fora do HTTP (gRPC ou mensageria).

    Equivale à injeção de dependências do FastAPI: em memória, reusa o repositório
    único; no postgres, abre uma sessão por chamada.
    """
    if state.session_factory is None:
        yield state.stock_repo
        return
    from estoque.infrastructure.database.repository import PostgresStockRepository
    async with state.session_factory() as session:
        yield PostgresStockRepository(session)
