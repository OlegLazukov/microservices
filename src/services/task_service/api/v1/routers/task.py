from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from src.services.task_service.api.v1.services.task import TaskService
from src.services.task_service.schemas.task import TaskResponse, TaskListResponse, TaskUpdateRequest, TaskCreateRequest

router_task = APIRouter()

@router_task.post(
    path='/',
    status_code=201,
    response_model=TaskResponse
)
async def create_task(
    task_data: TaskCreateRequest,
    service: TaskService = Depends(TaskService),
) -> TaskResponse:
    """Создает новую задачу."""
    created_task_response = await service.create_task(task_data)
    return created_task_response

@router_task.get(
    path='/{task_id}',
    status_code=200,
    response_model=TaskResponse
)
async def get_task(
    task_id: UUID4,
    service: TaskService = Depends(TaskService),
)-> TaskResponse:
    """Получает задачу по ID."""
    task_response = await service.get_task(task_id)
    if not task_response:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_response

@router_task.put(
    path='/{task_id}',
    status_code=200,
    response_model=TaskResponse
)
async def update_task(
    task_id: UUID4,
    task_data: TaskUpdateRequest,
    service: TaskService = Depends(TaskService),
) -> TaskResponse:
    """Обновляет задачу по ID."""
    updated_task_response = await service.update_task(task_id, task_data)
    if not updated_task_response:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task_response

@router_task.delete(
    path='/{task_id}',
    status_code=204
)
async def delete_task(
    task_id: UUID4,
    service: TaskService = Depends(TaskService),
) -> None:
    """Удаляет задачу по ID."""
    await service.delete_task(task_id)

@router_task.get(
    path='/',
    status_code=200,
    response_model=TaskListResponse
)
async def get_all_tasks(
    service: TaskService = Depends(TaskService),
    status: str | None = None,
) -> TaskListResponse:
    """Получает список всех задач."""
    tasks_list_response = await service.get_all_tasks(status=status)
    return tasks_list_response

