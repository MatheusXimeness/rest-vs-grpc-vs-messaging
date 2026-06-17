from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from usuario.application.ports.outbound import IUserRepository
from usuario.domain.user import User
from usuario.infrastructure.database.models import UserModel


class PostgresUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> None:
        model = UserModel(id=user.id, name=user.name, email=user.email)
        self._session.add(model)
        await self._session.commit()

    async def find_by_id(self, user_id: str) -> User | None:
        result = await self._session.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return User(id=model.id, name=model.name, email=model.email)

    async def find_all(self) -> list[User]:
        result = await self._session.execute(select(UserModel))
        return [User(id=m.id, name=m.name, email=m.email) for m in result.scalars()]
