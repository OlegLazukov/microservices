from pydantic import BaseModel, UUID4, EmailStr
from typing import List, Optional


class UserCreateRequest(BaseModel):
    full_name: Optional[str] = None
    password: str
    email: EmailStr

class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None

class UserFilters(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None


class UserDB(BaseModel):
    id: UUID4
    full_name: str
    email: str
    executing_tasks_count: Optional[int] = None
    watching_tasks_count: Optional[int] = None


class CreateUserResponse(BaseModel):
    payload: UserDB

class UserResponse(BaseModel):
    payload: UserDB | None

class UsersListResponse(BaseModel):
    payload: List[UserDB]

class UserTasksCountResponse(BaseModel):
    id: UUID4
    executing: Optional[int] = None
    watching: Optional[int] = None