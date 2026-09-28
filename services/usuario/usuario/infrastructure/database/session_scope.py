from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from usuario.application.ports.outbound import IUserRepository


@asynccontextmanager
async def repository_scope(state) -> AsyncIterator[IUserRepository]:
    """Repositório para uma chamada recebida fora do HTTP (gRPC ou mensageria).

    Equivale à injeção de dependências do FastAPI: em memória, reusa o repositório
    único; no postgres, abre uma sessão por chamada.
    """
    if state.session_factory is None:
        yield state.user_repo
        return
    from usuario.infrastructure.database.repository import PostgresUserRepository
    async with state.session_factory() as session:
        yield PostgresUserRepository(session)
