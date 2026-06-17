from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from usuario.domain.user import User


@dataclass
class GetUserQuery:
    user_id: str


@dataclass
class CreateUserCommand:
    id: str
    name: str
    email: str


class IGetUserUseCase(ABC):
    @abstractmethod
    async def execute(self, query: GetUserQuery) -> User: ...


class ICreateUserUseCase(ABC):
    @abstractmethod
    async def execute(self, command: CreateUserCommand) -> User: ...
