import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.services.auth_service.api.v1 import router
from src.services.auth_service.config import settings
from src.shared.rabbitmq import RabbitMQClient
from src.services.email_service.events.rabbitmq_consumer import EmailRabbitMQConsumer
from src.services.task_service.events.rabbitmq_consumer import RabbitMQConsumer


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """Инициализация RabbitMQ при запуске"""
#     try:
#
#     except:
#         logger.exception("Ошибка при инициализации RabbitMQ")
#         raise
#     yield
#     logger.info("Останавливаем RabbitMQ консьюмеры и закрываем клиент...")

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
    EmailRabbitMQConsumer.setup_rabbitmq_consumers(rabbitmq_client)
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="info")
