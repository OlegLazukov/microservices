from src.services.email_service.config import settings
from src.services.email_service.events import EmailRabbitMQConsumer
from src.shared.rabbitmq import RabbitMQClient

if __name__ == "__main__":
    rabbitmq_client = RabbitMQClient(settings.rabbitmq_url)
    EmailRabbitMQConsumer.setup_rabbitmq_consumers(rabbitmq_client)