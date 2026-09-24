"""Обработчики событий"""
__all__ = ["RabbitMQPublisher",
           "RabbitMQConsumer"]

from .rabbitmq_publisher import RabbitMQPublisher
from .rabbitmq_consumer import RabbitMQConsumer

