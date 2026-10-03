from typing import Dict

from fastapi import APIRouter, Depends, Request

from src.gateway.config import settings
from src.gateway.schemas.root import ApiGatewayInfo, ServicesUrls
from src.gateway.services.auth import AuthService
from src.gateway.services.task import TaskService
from src.gateway.services.user import UserService
from src.services.auth_service.schemas.auth import LoginRequest
from src.services.auth_service.schemas.user import UserCreateRequest, UserDB
from src.services.task_service.schemas.task import TaskCreateRequest, TaskResponse

router_gateway = APIRouter()



@router_gateway.get(
    path="/",
    status_code=201,
    response_model=ApiGatewayInfo,
)
async def root():
    """Корневой endpoint"""
    return ApiGatewayInfo(
        services=ServicesUrls(
            services_auth=settings.auth_service_url,
            services_task=settings.task_service_url,
        ))

@router_gateway.get("/health")
async def health():
    """Health check"""
    return {"status": "healthy"}


# ========== Auth Routes ==========
@router_gateway.post(
    path="/api/v1/auth/register",
    status_code=201,
    response_model=UserDB
                     )
async def register(
    user_data: UserCreateRequest,
    auth: AuthService = Depends()
) -> Dict:
    return await auth.register(user_data)



@router_gateway.post(
    path="/api/v1/auth/login",
    status_code=200
)
async def login(
    login_data: LoginRequest,
    auth: AuthService = Depends()
) -> Dict:
    return await auth.login(login_data)


# --- User Routes---
@router_gateway.get(
    path="/api/v1/users/current_user/",
    status_code=200
)
async def get_current_user_info(
        request: Request,
        service: UserService = Depends()
) -> Dict:
    return await service.get_current_user(request)


# --- Task Routes ---
@router_gateway.post(
    path="/api/v1/orders",
    status_code=201,
    response_model=TaskResponse
)
async def create_task(
        request: Request,
        task_data: TaskCreateRequest,
        service: TaskService = Depends()
) -> Dict:

    return await service.create_task(task_data, request)



@router_gateway.get(
    path="/api/v1/orders",
    status_code=200,
    response_model=TaskResponse
)
async def list_tasks(
        request: Request,
        service: TaskService = Depends()
) -> Dict:
    return await service.list_tasks(request)


@router_gateway.get(
    path="/api/v1/orders/{order_id}",
    status_code=200,
    response_model=TaskResponse
)
async def get_task(
        task_id: int,
        request: Request,
        service: TaskService = Depends()
) -> Dict:
    return await service.get_task_by_id(task_id, request)