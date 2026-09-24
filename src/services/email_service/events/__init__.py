"""Обработчики событий"""
from src.services.email_service.events.rabbitmq_consumer import EmailRabbitMQConsumer

__all__ = ["EmailRabbitMQConsumer"]