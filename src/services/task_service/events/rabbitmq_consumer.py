from src.services.task_service.api.v1.services.task import TaskService
from src.services.task_service.events import RabbitMQPublisher
from src.shared.rabbitmq import RabbitMQClient, logger



class RabbitMQConsumer(TaskService):
    _rabbitmq_publisher = RabbitMQPublisher()


    def handle_login_users_event(self, message: dict):
        """Обработчик события входа пользователя"""
        try:
            user_id = message.get('user_id')
            logger.info(f"Пользователь  с ID :{user_id}\n является авторизованным.")
            tasks_count_response = self.get_user_tasks_count(user_id)
            self._rabbitmq_publisher.publish_task_response_event("user_data", tasks_count_response)

        except Exception as e:
            logger.exception(f"Ошибка обработки события регистрации пользователя: {e}")
            raise


    @staticmethod
    def setup_rabbitmq_consumers(rabbitmq_client: RabbitMQClient):
        """Настройка потребителей RabbitMQ"""
        try:
            # Очередь для регистрации пользователей
            rabbitmq_client.declare_queue("task.count_requests")
            rabbitmq_client.bind_queue(
                "task.count_requests",
                "task_exchange",
                "user_logged_in",
                "direct"
            )

            # Запуск потребителя для событий получения данных
            # авторизованных пользователей
            rabbitmq_client.start_consumer_thread(
                queue_name="task.count_requests",
                callback=RabbitMQConsumer.handle_login_users_event,
                auto_ack=False
            )
            logger.info("RabbitMQ consumer запущен для task.count_requests")

        except Exception as e:
            logger.exception(f"Ошибка инициализации RabbitMQ: {e}")
            raise