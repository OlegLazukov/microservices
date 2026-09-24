from fastapi import HTTPException
from pydantic import UUID4

from src.services.task_service.schemas.task import UserTasksCountResponse
from src.services.task_service.repositories.task import TaskRepository
from src.services.task_service.schemas.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse, TaskListResponse
from src.services.task_service.models.task import Task
from src.services.task_service.utils.constants import TASK_EXIST_MSG, TASK_NOT_FOUND_MSG, TASK_FAIL_MSG
from src.services.task_service.utils.service import BaseService, transaction_mode


class TaskService(BaseService, TaskRepository):
    _repo: str = "task"

    @transaction_mode(auto_flush=True)
    async def create_task(self, task_data: TaskCreateRequest) -> TaskResponse:
        existing_task = await self.uow.task.get_by_name(title=task_data.title)
        if existing_task:
            raise HTTPException(status_code=409, detail=TASK_EXIST_MSG)

        task_data_dict = task_data.model_dump(exclude_unset=True, exclude={'observer_ids'})

        new_task_sa: Task = await self.add_one_and_get_obj(**task_data_dict)


        task_create = await self.uow.task.get_by_id(new_task_sa.id)
        if not task_create:
            raise HTTPException(status_code=500, detail=TASK_FAIL_MSG)

        return task_create.to_task_response_schema()

    @transaction_mode
    async def get_task(self, task_id: UUID4) -> TaskResponse | None:
        task_sa = await self.uow.task.get_by_id(task_id)
        self.check_existence(task_sa, details=TASK_NOT_FOUND_MSG)
        return task_sa.to_task_response_schema()

    @transaction_mode
    async def get_all_tasks(self, status: str | None = None) -> TaskListResponse:
        tasks_sa = await self.uow.task.get_all()
        filtered_tasks = []
        for task in tasks_sa:
            if status is not None and str(task.status.value) != status:
                continue
            filtered_tasks.append(task)
        return TaskListResponse(tasks=[task.to_task_response_schema() for task in filtered_tasks])

    @transaction_mode(auto_flush=True)
    async def update_task(self, task_id: UUID4, task_data: TaskUpdateRequest) -> TaskResponse | None:
        existing_task_sa = await self.uow.task.get_by_id(task_id)
        self.check_existence(existing_task_sa, details=TASK_NOT_FOUND_MSG)

        update_data = task_data.model_dump(exclude_unset=True)

        fields_to_update = {k: v for k, v in update_data.items() if
                            k not in ['author_id', 'executor_id', 'observer_ids']}

        update_task_sa: Task = await self.update_one_by_id(obj_id=task_id, **fields_to_update)

        task_update = await self.uow.task.get_by_id(update_task_sa.id)
        if not task_update:
            raise HTTPException(status_code=500, detail=TASK_FAIL_MSG)

        return task_update.to_task_response_schema()

    @transaction_mode
    async def delete_task(self, task_id: UUID4) -> None:
        existing_task = await self.get_by_filter_one_or_none(id=task_id)
        self.check_existence(existing_task, details=TASK_NOT_FOUND_MSG)

        await self.delete_by_ids(task_id)


    def get_user_tasks_count(self, user_id: UUID4) -> UserTasksCountResponse:
        executing_count = self.uow.task.count_tasks_by_executor(user_id)

        watching_count = self.uow.task.count_tasks_by_observer(user_id)
        resp = UserTasksCountResponse(
            id=user_id,
            executing=executing_count,
            watching=watching_count
        )
        return resp