from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from usuario.application.ports.inbound import CreateUserCommand, GetUserQuery
from usuario.application.use_cases.create_user import CreateUserUseCase
from usuario.application.use_cases.get_user import GetUserUseCase, ListUsersUseCase
from usuario.domain.exceptions import UserAlreadyExistsError, UserNotFoundError
from usuario.infrastructure.http.dependencies import (
    get_create_user_use_case,
    get_get_user_use_case,
    get_list_users_use_case,
)
from usuario.infrastructure.http.schemas import CreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: CreateUserRequest,
    use_case: CreateUserUseCase = Depends(get_create_user_use_case),
) -> UserResponse:
    try:
        user = await use_case.execute(CreateUserCommand(id=body.id, name=body.name, email=body.email))
        return UserResponse(id=user.id, name=user.name, email=user.email)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    use_case: GetUserUseCase = Depends(get_get_user_use_case),
) -> UserResponse:
    try:
        user = await use_case.execute(GetUserQuery(user_id=user_id))
        return UserResponse(id=user.id, name=user.name, email=user.email)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.get("", response_model=list[UserResponse])
async def list_users(
    use_case: ListUsersUseCase = Depends(get_list_users_use_case),
) -> list[UserResponse]:
    users = await use_case.execute()
    return [UserResponse(id=u.id, name=u.name, email=u.email) for u in users]
