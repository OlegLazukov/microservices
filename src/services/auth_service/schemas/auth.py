from typing import Optional
from pydantic import BaseModel, UUID4


class LoginRequest(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    user_id: UUID4
    email: Optional[str] = None