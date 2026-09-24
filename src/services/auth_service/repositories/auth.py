from typing import Optional
from sqlalchemy import select
from src.services.auth_service.models.user import User
from src.services.auth_service.utils.repository import SqlAlchemyRepository

class AuthRepository(SqlAlchemyRepository[User]):
    _model = User

    async def get_active_user(self, email: str) -> Optional[User]:
        """Получение активного пользователя по email."""
        query = select(self._model).filter_by(email=email)
        res = await self._session.execute(query)
        return res.scalar_one_or_none()


