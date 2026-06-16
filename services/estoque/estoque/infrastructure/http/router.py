from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from estoque.application.ports.inbound import (
    GetStockQuery,
    ReleaseStockCommand,
    ReserveStockCommand,
)
from estoque.application.use_cases.get_stock import GetStockUseCase, ListStockUseCase
from estoque.application.use_cases.release_stock import ReleaseStockUseCase
from estoque.application.use_cases.reserve_stock import ReserveStockUseCase
from estoque.domain.exceptions import InsufficientStockError, ProductNotFoundError
from estoque.infrastructure.http.dependencies import (
    get_get_stock_use_case,
    get_list_stock_use_case,
    get_release_use_case,
    get_reserve_use_case,
)
from estoque.infrastructure.http.schemas import (
    ReserveStockResponse,
    StockOperationRequest,
    StockResponse,
)

router = APIRouter(prefix="/stock", tags=["stock"])


@router.post("/reserve", response_model=ReserveStockResponse)
async def reserve_stock(
    body: StockOperationRequest,
    use_case: ReserveStockUseCase = Depends(get_reserve_use_case),
) -> ReserveStockResponse:
    try:
        await use_case.execute(ReserveStockCommand(
            product_id=body.product_id,
            quantity=body.quantity,
        ))
        return ReserveStockResponse(
            product_id=body.product_id,
            quantity=body.quantity,
            reserved=True,
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except InsufficientStockError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))


@router.post("/release")
async def release_stock(
    body: StockOperationRequest,
    use_case: ReleaseStockUseCase = Depends(get_release_use_case),
) -> dict:
    try:
        await use_case.execute(ReleaseStockCommand(
            product_id=body.product_id,
            quantity=body.quantity,
        ))
        return {"released": True}
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/{product_id}", response_model=StockResponse)
async def get_stock(
    product_id: str,
    use_case: GetStockUseCase = Depends(get_get_stock_use_case),
) -> StockResponse:
    try:
        stock = await use_case.execute(GetStockQuery(product_id=product_id))
        return StockResponse(
            product_id=stock.product_id,
            product_name=stock.product_name,
            quantity_available=stock.quantity_available,
            quantity_reserved=stock.quantity_reserved,
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("/", response_model=list[StockResponse])
async def list_stock(
    use_case: ListStockUseCase = Depends(get_list_stock_use_case),
) -> list[StockResponse]:
    stocks = await use_case.execute()
    return [
        StockResponse(
            product_id=s.product_id,
            product_name=s.product_name,
            quantity_available=s.quantity_available,
            quantity_reserved=s.quantity_reserved,
        )
        for s in stocks
    ]
