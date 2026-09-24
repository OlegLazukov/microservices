from src.shared.rabbitmq import RabbitMQClient, logger

class EmailRabbitMQConsumer:

    @staticmethod
    def handle_register_users_event(message: dict):
        """Обработчик события регистрации нового пользователя"""
        try:
            user_id = message.get('user_id')
            email = message.get('email')
            full_name = message.get('full_name')
            EmailRabbitMQConsumer.log_welcome_email(email, full_name)

            logger.info(f"Пользователь :{full_name} с ID :{user_id}\n зарегистрирован, приветственное письмо отправлено.")
        except Exception as e:
            logger.exception(f"Ошибка обработки события регистрации пользователя: {e}")
            raise

    @staticmethod
    def log_welcome_email(email: str, full_name: str):
        """Логирует приветственное письмо в консоль."""
        subject = "Добро пожаловать!"
        body = "Спасибо за регистрацию!"
        logger.info(f"Отправка письма на {email}: \n{subject} {full_name}\n{body}")

    @staticmethod
    def setup_rabbitmq_consumers(rabbitmq_client: RabbitMQClient):
        """Настройка потребителей RabbitMQ"""
        try:
            # Очередь для регистрации пользователей
            rabbitmq_client.declare_queue("email.notifications")
            rabbitmq_client.bind_queue(
                "email.notifications",
                "email_exchange",
                "user.registered",
                "direct"
            )

            # Запуск потребителя для событий регистрации пользователей
            rabbitmq_client.start_consumer_thread(
                queue_name="email.notifications",
                callback=EmailRabbitMQConsumer.handle_register_users_event,
                auto_ack=False
            )
            logger.info("RabbitMQ consumer запущен для email.notifications")

        except Exception as e:
            logger.exception(f"Ошибка инициализации RabbitMQ: {e}")
            raise