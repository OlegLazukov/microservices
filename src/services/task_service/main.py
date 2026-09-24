import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.services.auth_service.events.rabbitmq_consumer import RabbitMQConsumer
from src.services.task_service.api.v1 import router
from src.services.task_service.config import settings
from src.shared.rabbitmq import RabbitMQClient


def create_fast_api_app() -> FastAPI:
    fastapi_app = FastAPI()

    fastapi_app.include_router(router, prefix='/api')

    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return fastapi_app

app = create_fast_api_app()

if __name__ == "__main__":
    rabbitmq_client = RabbitMQClient(settings.rabbitmq_url)
    RabbitMQConsumer.setup_rabbitmq_consumers(rabbitmq_client)
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")