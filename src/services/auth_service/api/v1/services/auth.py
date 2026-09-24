from fastapi import HTTPException, status, Request
from datetime import timedelta

from fastapi.openapi.models import Response
from pydantic import UUID4

from src.services.auth_service.config import settings
from src.services.auth_service.events import RabbitMQPublisher

from src.services.auth_service.repositories.auth import AuthRepository
from src.services.auth_service.schemas.auth import Token, LoginRequest
from src.services.auth_service.schemas.user import UserDB, UserTasksCountResponse
from src.services.auth_service.utils.constants import USER_NOT_AUTH_MSG, USER_NOT_FOUND_MSG
from src.services.auth_service.utils.service import BaseService, transaction_mode
from src.services.auth_service.utils.auth import decode_access_token, create_access_token



class AuthService(BaseService, AuthRepository):
    _repo: str = "auth"
    _rabbitmq_publisher = RabbitMQPublisher()

    @transaction_mode
    async def login(self, response: Response, login_data: LoginRequest,
                    secret_key: str = settings.secret_key) -> Token:
        """Вход пользователя"""
        user = await self.uow.auth.get_active_user(email=login_data.email)

        if not user or not self.verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный email или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )


        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            secret_key=secret_key,
            expires_delta=access_token_expires,
        )
        response.set_cookie(key=settings.JWT_ACCESS_COOKIE_NAME, value=access_token, httponly=True, secure=True)
        return Token(access_token=access_token, token_type="bearer")

    @transaction_mode
    async def get_current_user(self, request: Request) -> UserDB:
        """Получение текущего пользователя из токена"""

        token = request.cookies[settings.JWT_ACCESS_COOKIE_NAME]

        if not token:
            raise HTTPException(
                status_code=401,
                detail=USER_NOT_AUTH_MSG,
                headers={"WWW-Authenticate": "Bearer"},
            )

        token_data = decode_access_token(token, settings.secret_key)

        if token_data is None:
            raise HTTPException(
                status_code=401,
                detail=USER_NOT_AUTH_MSG,
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self.uow.auth.get_active_user(email=token_data.email)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail=USER_NOT_FOUND_MSG,
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user.to_userdb_schema()


    @transaction_mode
    async def send_data_user(self, user_id: UUID4) -> UserDB:
        user = await self.get_by_filter_one_or_none(id=user_id)
        if user is None:
            raise HTTPException(
                status_code=404,
                detail=USER_NOT_FOUND_MSG,
                headers={"WWW-Authenticate": "Bearer"},
            )

        self._rabbitmq_publisher.publish_login_user_event("user_logged_in", user_id)
        return user.to_userdb_schema()


    @staticmethod
    async def get_data_count_task(data_count_task: UserTasksCountResponse) -> UserTasksCountResponse:

        if not data_count_task or not isinstance(data_count_task, UserTasksCountResponse):
            raise HTTPException(status_code=500, detail="Ошибка обработки данных о задачах пользователя.")

        return UserTasksCountResponse(
            id=data_count_task.id,
            executing=data_count_task.executing_count,
            watching=data_count_task.watching_count,
        )