from src.services.auth_service.api.v1.services.auth import AuthService
from src.services.auth_service.schemas.user import UserTasksCountResponse
from src.shared.rabbitmq import RabbitMQClient, logger



class RabbitMQConsumer(AuthService):


    def handle_data_users_event(self, message: UserTasksCountResponse):
        """Обработчик события количества задач пользователя"""
        try:
            tasks_count_response = UserTasksCountResponse(
                id=message.get('user_id'),
                executing=message.get('executing_count'),
                watching=message.get('watching_count')
            )
            logger.info(f"Пользователь  с ID :{tasks_count_response.id}\n "
                        f"имеет столько наблюдателей {tasks_count_response.watching} за задачей и столько является исполнителем {tasks_count_response.executing} задач.")

            self.uow.get_data_count_task(message)

        except Exception as e:
            logger.exception(f"Ошибка обработки события регистрации пользователя: {e}")
            raise


    @staticmethod
    def setup_rabbitmq_consumers(rabbitmq_client: RabbitMQClient):
        """Настройка потребителей RabbitMQ"""
        try:
            # Очередь для получения информации об авторизованном пользователе
            rabbitmq_client.declare_queue("task_count_response")
            rabbitmq_client.bind_queue(
                "task_count_response",
                "task_response_exchange",
                "user_data",
                "direct"
            )

            # Запуск потребителя для событий регистрации пользователей
            rabbitmq_client.start_consumer_thread(
                queue_name="task_count_response",
                callback=RabbitMQConsumer.handle_data_users_event,
                auto_ack=False
            )
            logger.info("RabbitMQ consumer запущен для task.task_count_response")

        except Exception as e:
            logger.exception(f"Ошибка инициализации RabbitMQ: {e}")
            raise