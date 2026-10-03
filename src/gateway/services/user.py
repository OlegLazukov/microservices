from typing import Dict, Any
from fastapi import HTTPException, Request
from src.gateway.utils.client import MicroserviceClient
from src.gateway.utils.constants import USER_NOT_FOUND_MSG, TOKEN_NOT_VALID_MSG
from src.gateway.utils.token import Token


class UserService(MicroserviceClient, Token):

    async def get_current_user(self, request: Request) -> Dict[str, Any]:
        token = self.extract_token(request)

        if not token:
            raise HTTPException(status_code=401, detail=TOKEN_NOT_VALID_MSG)

        user = await self.get(
            "/api/users/current_user/",
            headers={"Authorization": f"Bearer {token}"},
        )
        if not user:
            raise HTTPException(status_code=401, detail=USER_NOT_FOUND_MSG)

        return user

