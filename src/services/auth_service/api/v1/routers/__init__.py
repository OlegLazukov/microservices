__all__ = [
    'v1_router_user',
    'v1_router_auth',
]

from src.services.auth_service.api.v1.routers.user import router_user as v1_router_user
from src.services.auth_service.api.v1.routers.auth import router_auth as v1_router_auth
