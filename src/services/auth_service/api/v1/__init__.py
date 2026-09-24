__all__ = [
    'router'
]


from fastapi import APIRouter
from src.services.auth_service.api.v1.routers import user, auth


router = APIRouter()


router.include_router(user.router_user, prefix='/users', tags=['User | v1'])
router.include_router(auth.router_auth, prefix='/auth', tags=['Auth | v1'])



