from src.services.task_service.config import settings
from src.services.auth_service.schemas.user import UserTasksCountResponse
from src.shared.rabbitmq import RabbitMQClient, logger


class RabbitMQPublisher:
    """Класс для публикации событий в RabbitMQ"""

    def __init__(self):
        self._client = None

    @property
    def client(self) -> RabbitMQClient:
        """Получить клиент RabbitMQ (lazy initialization)"""
        try:
            if self._client is None:
                self._client = RabbitMQClient(settings.rabbitmq_url)
                self._setup_queues()
            return self._client
        except Exception as e:
            logger.exception(f"Ошибка настройки клиента: {e}")
            raise


    def _setup_queues(self):
        """Настройка очередей для публикации"""
        try:
            self._client.declare_queue("task_count_response")
            self._client.bind_queue(
                "task_count_response",
                "task_response_exchange",
                "user_data",
                "direct"
            )
        except Exception as e:
            logger.exception(f"Ошибка настройки очередей RabbitMQ: {e}")
            raise


    def publish_task_response_event(self, event_type: str, user: UserTasksCountResponse):
        """Публикация данных по количеству задач авторизованного пользователя"""

        message = {
            "type": "user_data",
            "data": {
                "user_id": str(user.id),
                "executing_count": user.executing_tasks_count,
                "watching_count": user.watching_tasks_count
            },
        }

        try:
            self.client.publish_message(
                exchange="task_response_exchange",
                routing_key=event_type,
                message=message,
                exchange_type="direct",
            )
            logger.info(f"Событие {event_type} опубликовано для пользователя {user.id}")
        except Exception as e:
            logger.exception(f"Ошибка публикации события {event_type}: {e}")
            raise
