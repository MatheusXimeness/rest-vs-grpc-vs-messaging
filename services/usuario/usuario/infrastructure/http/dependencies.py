from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from usuario.application.ports.outbound import IUserRepository
from usuario.application.use_cases.create_user import CreateUserUseCase
from usuario.application.use_cases.get_user import GetUserUseCase, ListUsersUseCase


async def _get_db(request: Request) -> AsyncGenerator[AsyncSession | None, None]:
    if request.app.state.session_factory is None:
        yield None
        return
    async with request.app.state.session_factory() as session:
        yield session


def get_user_repo(request: Request, session: AsyncSession = Depends(_get_db)) -> IUserRepository:
    if request.app.state.settings.USE_IN_MEMORY_DB:
        return request.app.state.user_repo
    from usuario.infrastructure.database.repository import PostgresUserRepository
    return PostgresUserRepository(session)


def get_get_user_use_case(repo: IUserRepository = Depends(get_user_repo)) -> GetUserUseCase:
    return GetUserUseCase(repo)


def get_create_user_use_case(repo: IUserRepository = Depends(get_user_repo)) -> CreateUserUseCase:
    return CreateUserUseCase(repo)


def get_list_users_use_case(repo: IUserRepository = Depends(get_user_repo)) -> ListUsersUseCase:
    return ListUsersUseCase(repo)
