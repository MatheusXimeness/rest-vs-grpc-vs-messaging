from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from estoque.application.ports.outbound import IStockRepository
from estoque.application.use_cases.get_stock import GetStockUseCase, ListStockUseCase
from estoque.application.use_cases.release_stock import ReleaseStockUseCase
from estoque.application.use_cases.reserve_stock import ReserveStockUseCase


async def _get_db(request: Request) -> AsyncGenerator[AsyncSession | None, None]:
    if request.app.state.session_factory is None:
        yield None
        return
    async with request.app.state.session_factory() as session:
        yield session


def get_stock_repo(request: Request, session: AsyncSession = Depends(_get_db)) -> IStockRepository:
    if request.app.state.settings.USE_IN_MEMORY_DB:
        return request.app.state.stock_repo
    from estoque.infrastructure.database.repository import PostgresStockRepository
    return PostgresStockRepository(session)


def get_reserve_use_case(repo: IStockRepository = Depends(get_stock_repo)) -> ReserveStockUseCase:
    return ReserveStockUseCase(repo)


def get_release_use_case(repo: IStockRepository = Depends(get_stock_repo)) -> ReleaseStockUseCase:
    return ReleaseStockUseCase(repo)


def get_get_stock_use_case(repo: IStockRepository = Depends(get_stock_repo)) -> GetStockUseCase:
    return GetStockUseCase(repo)


def get_list_stock_use_case(repo: IStockRepository = Depends(get_stock_repo)) -> ListStockUseCase:
    return ListStockUseCase(repo)
