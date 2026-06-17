from __future__ import annotations

from usuario.application.ports.inbound import CreateUserCommand, ICreateUserUseCase
from usuario.application.ports.outbound import IUserRepository
from usuario.domain.exceptions import UserAlreadyExistsError
from usuario.domain.user import User


class CreateUserUseCase(ICreateUserUseCase):
    def __init__(self, repo: IUserRepository) -> None:
        self._repo = repo

    async def execute(self, command: CreateUserCommand) -> User:
        existing = await self._repo.find_by_id(command.id)
        if existing is not None:
            raise UserAlreadyExistsError(f"User '{command.id}' already exists")
        user = User(id=command.id, name=command.name, email=command.email)
        await self._repo.save(user)
        return user
