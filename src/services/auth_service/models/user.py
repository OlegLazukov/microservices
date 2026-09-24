import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Annotated
from src.services.auth_service.schemas.user import UserDB
from src.services.auth_service.schemas.user import UserTasksCountResponse

Base = declarative_base()

int_pk = Annotated[UUID ,mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
str_name_uq = Annotated[str, mapped_column(String(100), nullable=False, unique=True)]
str_name = Annotated[str, mapped_column(String(100), nullable=False)]



class User(Base):
    __tablename__ = 'users'

    id: Mapped[int_pk]
    full_name: Mapped[str_name]
    password = mapped_column(String, nullable=False, unique=True)
    hashed_password = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False)

    executing_tasks_count: int = 0
    watching_tasks_count: int = 0

    def to_userdb_schema(self) -> "UserDB":
        return UserDB(
            id=self.id,
            full_name=self.full_name,
            email=self.email,
            created_at=self.created_at,
            executing_tasks_count=self.executing_tasks_count,
            watching_tasks_count=self.watching_tasks_count,
        )

    def to_userdb_count_tasks(self) -> "UserTasksCountResponse":
        return UserTasksCountResponse(
            id=self.id,
            executing=self.executing_tasks_count,
            watching=self.watching_tasks_count
        )