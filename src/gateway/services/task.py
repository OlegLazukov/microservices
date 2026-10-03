from typing import Dict, Any
from fastapi import HTTPException, Request
from src.gateway.utils.client import MicroserviceClient
from src.gateway.utils.constants import TOKEN_NOT_VALID_MSG
from src.gateway.utils.token import Token
from src.services.task_service.schemas.task import TaskCreateRequest


class TaskService(MicroserviceClient, Token):

    async def create_task(self, payload: TaskCreateRequest, request: Request) -> Dict[str, Any]:
        token = self.extract_token(request)
        if not token:
            raise HTTPException(status_code=401, detail=TOKEN_NOT_VALID_MSG)
        payload_dict = payload.model_dump()

        return await self.post(
            "/api/tasks",
            json_data=payload_dict,
            headers={"Authorization": f"Bearer {token}"},
        )

    async def list_tasks(self, request: Request) -> Dict[str, Any]:
        token = self.extract_token(request)
        if not token:
            raise HTTPException(status_code=401, detail=TOKEN_NOT_VALID_MSG)
        return await self.get(
            "/api/tasks",
            headers={"Authorization": f"Bearer {token}"},
        )

    async def get_task_by_id(self, task_id: int, request: Request) -> Dict[str, Any]:
        token = self.extract_token(request)
        if not token:
            raise HTTPException(status_code=401, detail=TOKEN_NOT_VALID_MSG)
        return await self.get(
            f"/api/tasks/{task_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
