
from fastapi import APIRouter, Depends
from pydantic import UUID4

from src.services.auth_service.api.v1.services.user import UserService
from src.services.auth_service.schemas.user import (
    UserCreateRequest,
    UserUpdateRequest,
    UserFilters,
    UsersListResponse,
    UserResponse,
    CreateUserResponse,
    UserDB
)

router_user = APIRouter(prefix='/users')

@router_user.post(
    path='/',
    status_code=201,
    response_model=CreateUserResponse,
)
async def create_user(
    user_data: UserCreateRequest,
    service: UserService = Depends(UserService),
) -> CreateUserResponse:
    """Создает нового пользователя."""
    created_user: UserDB = await service.create_user(user_data)
    return CreateUserResponse(payload=created_user)

@router_user.get(
    path='/{user_id}',
    status_code=200,
    response_model=UserResponse,
)
async def get_user(
    user_id: UUID4,
    service: UserService = Depends(UserService),
) -> UserResponse:
    """Получает пользователя по ID."""
    user: UserDB | None = await service.get_user(user_id)
    return UserResponse(payload=user)

@router_user.put(
    path='/{user_id}',
    status_code=200,
    response_model=UserResponse,
)
async def update_user(
    user_id: UUID4,
    user_data: UserUpdateRequest,
    service: UserService = Depends(UserService),
) -> UserResponse:
    """Обновляет пользователя по ID."""
    updated_user: UserDB = await service.update_user(user_id, user_data)
    return UserResponse(payload=updated_user)

@router_user.delete(
    path='/{user_id}',
    status_code=204,
)
async def delete_user(
    user_id: UUID4,
    service: UserService = Depends(UserService),
) -> None:
    """Удаляет пользователя по ID."""
    await service.delete_user(user_id)

@router_user.get(
    path='/filters/',
    status_code=200,
    response_model=UsersListResponse,
)
async def get_users_by_filters(
    filters: UserFilters = Depends(),
    service: UserService = Depends(UserService),
) -> UsersListResponse:
    """Получает список пользователей по фильтрам."""
    users = await service.get_users_by_filters(filters)
    return UsersListResponse(payload=users)