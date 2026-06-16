from __future__ import annotations

from pedidos.application.ports.outbound import IUserServicePort, UserInfo
from pedidos.domain.exceptions import UserNotFoundError

_USERS: dict[str, UserInfo] = {
    "user-1": UserInfo(id="user-1", name="Alice Silva", email="alice@example.com"),
    "user-2": UserInfo(id="user-2", name="Bob Souza", email="bob@example.com"),
    "user-3": UserInfo(id="user-3", name="Carol Lima", email="carol@example.com"),
}


class UserStubAdapter(IUserServicePort):
    async def get_user(self, user_id: str) -> UserInfo:
        if user_id not in _USERS:
            raise UserNotFoundError(f"User '{user_id}' not found")
        return _USERS[user_id]
