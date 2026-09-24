from fastapi import HTTPException, BackgroundTasks
from pydantic import UUID4

from src.services.auth_service.events import RabbitMQPublisher
from src.services.auth_service.repositories import UserRepository
from src.services.auth_service.schemas.user import UserCreateRequest, UserUpdateRequest, UserFilters, UserDB
from src.services.auth_service.models.user import User
from src.services.auth_service.utils.constants import USER_EXIST_MSG, USER_NOT_FOUND_MSG
from src.services.auth_service.utils.service import transaction_mode, BaseService

class UserService(BaseService, UserRepository):
    _repo: str = "user"
    _rabbit_publisher = RabbitMQPublisher()
    bg = BackgroundTasks()

    @transaction_mode
    async def create_user(self, user_data: UserCreateRequest) -> UserDB:
        existing_user_by_email = await self.uow.user.get_by_email(email=user_data.email)

        if existing_user_by_email:
            raise HTTPException(status_code=409, detail=USER_EXIST_MSG)
        hashed_password = self.get_password_hash(user_data.password)

        created_user_sa: User = await self.add_one_and_get_obj(
            **user_data.model_dump(exclude={"password", "hashed_password"}),
            password=user_data.password,
            hashed_password=hashed_password
        )


        self._rabbit_publisher.publish_register_user_event("user_registered", created_user_sa)
        return created_user_sa.to_userdb_schema()


    @transaction_mode
    async def get_user(self, user_id: UUID4) -> UserDB | None:
        user_sa = await self.get_by_filter_one_or_none(id=user_id)
        self.check_existence(user_sa, details=USER_NOT_FOUND_MSG)
        return user_sa.to_userdb_schema()

    @transaction_mode
    async def get_all_users(self) -> list[UserDB]:
        users_sa = await self.get_by_filter_all()
        return [user.to_userdb_schema() for user in users_sa]

    @transaction_mode
    async def update_user(self, user_id: UUID4, user_data: UserUpdateRequest) -> UserDB:
        existing_user_sa = await self.get_by_filter_one_or_none(id=user_id)
        self.check_existence(existing_user_sa, details=USER_NOT_FOUND_MSG)

        update_data = user_data.model_dump(exclude_unset=True)

        if 'email' in update_data and update_data['email'] != existing_user_sa.email:
            existing_user_by_email = await self.uow.user.get_by_email(email=update_data['email'])
            if existing_user_by_email:
                raise HTTPException(status_code=409, detail="User with this email already exists")

        if 'password' in update_data:
            update_data['password'] = self.get_password_hash(password=update_data['password'])


        updated_user_sa: User = await self.update_one_by_id(obj_id=user_id, **update_data)
        self.check_existence(updated_user_sa, details=f"Failed to update user with id {user_id}")
        return updated_user_sa.to_userdb_schema()

    @transaction_mode
    async def get_users_by_filters(self, filters: UserFilters) -> list[UserDB]:
        users_sa = await self.uow.user.get_by_filters(**filters.model_dump())
        return [user.to_userdb_schema() for user in users_sa]


    @transaction_mode
    async def delete_user(self, user_id: UUID4) -> None:
        existing_user = await self.get_by_filter_one_or_none(id=user_id)
        self.check_existence(existing_user, details=USER_NOT_FOUND_MSG)

        await self.delete_by_ids(user_id)

