from pydantic import UUID4

from src.services.auth_service.config import settings
from src.services.auth_service.models.user import User
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
            # Очереди для резервирования
            self._client.declare_queue("email.notifications")
            self._client.declare_queue("task_count_requests")
            self._client.bind_queue(
                "email.notifications",
                "email_exchange",
                "user.registered",
                "direct"
            )
            self._client.bind_queue(
                "task.count_requests",
                "task_exchange",
                "user_logged_in",
                "direct"
            )
        except Exception as e:
            logger.exception(f"Ошибка настройки очередей RabbitMQ: {e}")
            raise

    def publish_register_user_event(self, event_type: str, user: User):
        """Публикация события о регистрации"""

        message = {
            "type": "user_registered",
            "data": {
                "user_id": str(user.id),
                "email": user.email,
            },
        }

        try:
            self.client.publish_message(
                exchange="email_exchange",
                routing_key=event_type,
                message=message,
                exchange_type="direct",
            )
            logger.info(f"Событие {event_type} опубликовано для пользователя {user.id}")
        except Exception as e:
            logger.exception(f"Ошибка публикации события {event_type}: {e}")
            raise

    def publish_login_user_event(self, event_type: str, user_id: UUID4):
        """Публикация авторизации пользователя"""

        message = {
            "type": "user_logged_in",
            "data": {
                "user_id": str(user_id),
            },
        }

        try:
            self.client.publish_message(
                exchange="task_exchange",
                routing_key=event_type,
                message=message,
                exchange_type="direct",
            )
            logger.info(f"Событие {event_type} опубликовано для пользователя {user_id}")
        except Exception as e:
            logger.exception(f"Ошибка публикации события {event_type}: {e}")
            raise
