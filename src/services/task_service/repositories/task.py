from typing import Optional
from sqlalchemy import func
from sqlalchemy.future import select
from sqlalchemy.dialects.postgresql import UUID
from src.services.task_service.models.task import Task
from src.services.task_service.utils.repository import SqlAlchemyRepository


class TaskRepository(SqlAlchemyRepository[Task]):
    _model = Task

    async def get_by_name(self, title: str) -> Optional[Task]:
        query = select(self._model).filter_by(title=title)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()

    async def get_by_id(self, task_id: UUID) -> Optional[Task]:
        query = select(self._model).filter_by(id=task_id)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()

    async def get_all(self):
        query = select(self._model)
        res = await self._session.execute(query)
        return res.scalars().all()


    async def count_tasks_by_executor(self, user_id: UUID) -> int:
        query = select(func.count()).where(Task.executor_id == user_id)
        result = await self._session.execute(query)
        return result.scalar()

    async def count_tasks_by_observer(self, user_id: UUID) -> int:
        query = select(func.count()).where(Task.observer_ids.contains([user_id]))
        result = await self._session.execute(query)
        return result.scalar()

