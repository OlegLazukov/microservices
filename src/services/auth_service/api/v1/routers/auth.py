from fastapi import APIRouter, Depends, Response, Request
from pydantic import UUID4

from src.services.auth_service.api.v1.services.auth import AuthService
from src.services.auth_service.api.v1.services.user import UserService
from src.services.auth_service.schemas.auth import LoginRequest, Token
from src.services.auth_service.schemas.user import UserCreateRequest, UserDB, UserResponse, UserTasksCountResponse

router_auth = APIRouter()


@router_auth.post(
    path='/register',
    status_code=201,
    response_model=UserDB,
)
async def register(
    user_data: UserCreateRequest,
    user_service: UserService = Depends(UserService),
) -> UserDB:
    """Регистрация нового пользователя."""
    created_user: UserDB = await user_service.create_user(user_data)
    return created_user


@router_auth.post(
    path='/login',
    status_code=200,
    response_model=Token,
)
async def login(
    login_data: LoginRequest,
    response: Response,
    service: AuthService = Depends(AuthService),

) -> Token:
    """Аутентификация пользователя и получение токена."""
    return await service.login(response=response, login_data=login_data)


@router_auth.get(
    path='/current_user/',
    status_code=200,
)
async def get_current_user(
    request: Request,
    service: AuthService = Depends(AuthService),
) -> UserDB:
    """Получение текущего пользователя по токену из куки."""
    return await service.get_current_user(request)

@router_auth.get(
    path='/user/info/{user_id}',
    status_code=200,
    response_model=UserResponse
)
async def get_user_info(
        user_id: UUID4,
        auth_service: AuthService = Depends(AuthService),
):
    user : UserDB | None = await auth_service.send_data_user(user_id)
    user_tasks_count: UserTasksCountResponse = await auth_service.get_data_count_task(user.id)
    user.executing_tasks_count = user_tasks_count.executing
    user.watching_tasks_count = user_tasks_count.watching
    return UserResponse(payload=user)