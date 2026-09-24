from datetime import datetime, timedelta
from typing import Optional
from venv import logger
from jose import JWTError, jwt
import bcrypt

from src.services.auth_service.schemas.auth import TokenData

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверка пароля"""
    try:
        password_bytes = plain_password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    """Хеширование пароля"""
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def create_access_token(data: dict, secret_key: str, expires_delta: Optional[timedelta] = None) -> str:
    """Создание JWT токена"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def decode_access_token(token: str, secret_key: str) -> Optional[TokenData]:
    """Декодирование JWT токена"""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        logger.info(payload)
        user_id = payload.get("sub")
        email = payload.get("email")
        if user_id is None:
            return None
        # JWT хранит sub как строку, конвертируем в int
        token_data = TokenData(user_id=user_id, email=email)
        return token_data
    except (JWTError, ValueError, TypeError):
        return None