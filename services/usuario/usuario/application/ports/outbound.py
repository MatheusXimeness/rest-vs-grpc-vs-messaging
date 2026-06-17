from __future__ import annotations

from abc import ABC, abstractmethod

from usuario.domain.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def save(self, user: User) -> None: ...

    @abstractmethod
    async def find_by_id(self, user_id: str) -> User | None: ...

    @abstractmethod
    async def find_all(self) -> list[User]: ...
