"""Handlers das filas do serviço de usuário (contrato em communication/messaging/rabbitmq)."""
from __future__ import annotations

from usuario.application.ports.inbound import GetUserQuery
from usuario.application.use_cases.get_user import GetUserUseCase
from usuario.domain.exceptions import UserNotFoundError
from usuario.infrastructure.amqp.rpc_server import start_rpc_server
from usuario.infrastructure.database.session_scope import repository_scope


def _handlers(state) -> dict:
    async def get_user(payload: dict) -> dict:
        async with repository_scope(state) as repo:
            try:
                user = await GetUserUseCase(repo).execute(GetUserQuery(user_id=payload["user_id"]))
            except UserNotFoundError as exc:
                return {"status": 404, "detail": str(exc)}
        return {"status": 200, "id": user.id, "name": user.name, "email": user.email}

    return {"usuario.get_user": get_user}


async def start_consumer(state, url: str, prefetch: int):
    return await start_rpc_server(url, _handlers(state), prefetch)
