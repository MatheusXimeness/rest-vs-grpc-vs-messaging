from __future__ import annotations

from usuario.application.ports.inbound import GetUserQuery, IGetUserUseCase
from usuario.application.ports.outbound import IUserRepository
from usuario.domain.exceptions import UserNotFoundError
from usuario.domain.user import User


class GetUserUseCase(IGetUserUseCase):
    def __init__(self, repo: IUserRepository) -> None:
        self._repo = repo

    async def execute(self, query: GetUserQuery) -> User:
        user = await self._repo.find_by_id(query.user_id)
        if user is None:
            raise UserNotFoundError(f"User '{query.user_id}' not found")
        return user


class ListUsersUseCase:
    def __init__(self, repo: IUserRepository) -> None:
        self._repo = repo

    async def execute(self) -> list[User]:
        return await self._repo.find_all()
