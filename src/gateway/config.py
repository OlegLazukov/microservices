from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки Gateway"""
    auth_service_url: str = "http://auth-service:8000"
    task_service_url: str = "http://task-service:8000"
    email_service_url: str = "http://email-service:8000"

    class Config:
        env_file = ".env"


settings = Settings()