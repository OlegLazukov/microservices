__all__ = [
    'router'
]


from fastapi import APIRouter
from src.services.task_service.api.v1.routers import task


router = APIRouter()


router.include_router(task.router_task, prefix='/tasks', tags=['Task | v1'])



