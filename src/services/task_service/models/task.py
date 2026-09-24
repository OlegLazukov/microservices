import uuid
from sqlalchemy import String, Text, Index, text
from sqlalchemy.orm import Mapped, mapped_column, declarative_base
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Annotated, List
from src.services.task_service.schemas.task import TaskResponse
from src.services.task_service.enums.task_status import TaskStatus

Base = declarative_base()

int_pk = Annotated[UUID ,mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)]
str_name_uq = Annotated[str, mapped_column(String(100), nullable=False, unique=True)]
str_name = Annotated[str, mapped_column(String(100), nullable=False)]




class Task(Base):
    __tablename__ = 'task'
    __table_args__ = (Index('idx_task_author', "author_id"),)
    id: Mapped[int_pk]
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text)
    status: Mapped[TaskStatus] = mapped_column(String(50), nullable=False)
    executor_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), nullable=False)
    author_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    observers: Mapped[List[UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)


    def to_task_response_schema(self) -> "TaskResponse":

        return TaskResponse(
            id=self.id,
            title=self.title,
            description=self.description,
            status=self.status,
            created_at=self.created_at,
            executor_id=self.executor_id,
            author_id=self.author_id,
            observers=self.observers or []
        )
