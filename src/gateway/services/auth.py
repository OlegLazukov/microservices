from fastapi import HTTPException
from typing import Dict, Any
from src.gateway.utils.client import MicroserviceClient
from src.gateway.utils.constants import TOKEN_NOT_VALID_MSG, TOKEN_NOT_FOUND_MSG
from src.services.auth_service.schemas.auth import LoginRequest
from src.services.auth_service.schemas.user import UserCreateRequest


class AuthService(MicroserviceClient):

    async def register(self, payload: UserCreateRequest) -> Dict[str, Any]:
        payload_dict = payload.model_dump()
        return await self.post("/api/auth/register", json_data=payload_dict)

    async def login(self, payload: LoginRequest) -> Dict[str, Any]:
        payload_dict = payload.model_dump()
        return await self.post("/api/auth/login", json_data=payload_dict)

    async def verify_token(self, token: str) -> Dict[str, Any]:
        if not token:
            raise HTTPException(status_code=401, detail=TOKEN_NOT_FOUND_MSG)

        try:
            return await self.get(
                "/api/users/current_user/",
                headers={"Authorization": f"Bearer {token}"},
            )
        except Exception:
            raise HTTPException(status_code=401, detail=TOKEN_NOT_VALID_MSG)
