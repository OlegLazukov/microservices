from abc import ABC, abstractmethod
from types import TracebackType
from typing import Any, Never
from src.services.task_service.database.db import async_session_maker
from src.services.task_service.repositories.task import TaskRepository


class AbstractUnitOfWork(ABC):
    is_open: bool
    task: TaskRepository

    @abstractmethod
    def __init__(self) -> Never:
        raise NotImplementedError
    @abstractmethod
    async def __aenter__(self) -> Never:
        raise NotImplementedError
    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> Never:
        raise NotImplementedError
    @abstractmethod
    async def flush(self) -> Never:
        raise NotImplementedError
    @abstractmethod
    async def rollback(self) -> Never:
        raise NotImplementedError

class UnitOfWork(AbstractUnitOfWork):
    __slots__ = (
        "_session",
        "task",
    )
    def __init__(self) -> None:
        self.is_open = False

    async def __aenter__(self) -> None:
        self._session = async_session_maker()
        self.task = TaskRepository(self._session)
        self.is_open = True


    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_type is None:
            await self._session.commit()
        else:
            await self._session.rollback()
        await self._session.close()

    async def merge(self, obj: Any)-> None:
        await self._session.merge(obj)

    async def flush(self) -> None:
        await self._session.flush()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def session_add(self, obj: Any) -> None:
        self._session.add(obj)

    async def session_refresh(self, obj: Any) -> None:
        await self._session.refresh(obj)

    def __getattr__(self, name: str) -> Any:
        err_msg = f"'{self.__class__.__name__}' object has no attribute '{name}'"
        raise AttributeError(err_msg)