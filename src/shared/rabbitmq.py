"""
Общие утилиты для работы с RabbitMQ
"""
import json
import logging
import uuid
import time
import threading
from typing import Optional, Callable, Dict, Any
from pika import BlockingConnection, ConnectionParameters, PlainCredentials
from pika.exceptions import AMQPConnectionError
from contextlib import contextmanager
from pika import BasicProperties

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log"),
    ]
)
logger = logging.getLogger(__name__)

class RabbitMQClient:
    """Клиент для работы с RabbitMQ"""

    def __init__(self, rabbitmq_url: str):
        self.rabbitmq_url = rabbitmq_url
        self.connection: Optional[BlockingConnection] = None
        self._parse_url()

    def _parse_url(self):
        """Парсинг URL для получения параметров подключения"""
        url = self.rabbitmq_url.replace("amqp://", "")
        rest = None
        if "@" in url:
            creds, rest = url.split("@", 1)
            if ":" in creds:
                self.username, self.password = creds.split(":", 1)
            else:
                self.username = creds
                self.password = ""
        else:
            self.username = "guest"
            self.password = "guest"
            rest = url

        if "/" in rest:
            parts = rest.split("/", 1)
            host_port = parts[0]
            self.vhost = parts[1] if parts[1] else "/"
            if self.vhost != "/":
                self.vhost = self.vhost.replace("%2F", "/")
        else:
            host_port = rest
            self.vhost = "/"

        if ":" in host_port:
            self.host, port = host_port.split(":", 1)
            self.port = int(port)
        else:
            self.host = host_port
            self.port = 5672

    def _get_parameters(self) -> ConnectionParameters:
        """Возвращает ConnectionParameters из распарсенных значений"""
        credentials = PlainCredentials(self.username, self.password)
        return ConnectionParameters(
            host=self.host,
            port=self.port,
            virtual_host=self.vhost,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300,
        )

    def get_connection(self) -> BlockingConnection:
        """
        Подключается к RabbitMQ с retry и экспоненциальной задержкой.
        Возвращает готовое соединение (не контекстный менеджер).
        """
        params = self._get_parameters()
        max_retries = 10
        base_delay = 2

        for attempt in range(max_retries):
            try:
                conn = BlockingConnection(params)
                self.connection = conn
                logger.info(f"[RabbitMQ] Connected on attempt {attempt + 1}")
                return conn
            except AMQPConnectionError as e:
                if attempt == max_retries - 1:
                    logger.error(
                        f"[RabbitMQ] Failed to connect after {max_retries} attempts."
                    )
                    raise
                delay = base_delay * (2**attempt)
                logger.warning(
                    f"[RabbitMQ] Connection failed "
                    f"(attempt {attempt + 1}/{max_retries}), "
                    f"retrying in {delay}s: {e}"
                )
                time.sleep(delay)

    @contextmanager
    def channel(self):
        """
        Контекстный менеджер: создаёт канал из существующего
        или нового соединения, yields канал, закрывает канал после use.
        Соединение НЕ закрывает (оно переиспользуется).
        """
        if self.connection is None or not self.connection.is_open:
            self.get_connection()

        ch = self.connection.channel()
        try:
            yield ch
        finally:
            if ch.is_open:
                ch.close()

    def close(self):
        """Закрытие соединения"""
        if self.connection and self.connection.is_open:
            try:
                self.connection.close()
            except Exception:
                pass

    # ─── Публикация ───────────────────────────────────────────

    def publish_message(
        self,
        exchange: str,
        routing_key: str,
        message: Dict[Any, Any],
        exchange_type: str = "direct",
    ):
        """Публикация сообщения в очередь"""
        try:
            with self.channel() as ch:
                ch.exchange_declare(
                    exchange=exchange, exchange_type=exchange_type, durable=True
                )
                ch.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=json.dumps(message),
                    properties=BasicProperties(delivery_mode=2),
                )
                logger.info(f"Сообщение отправлено в {exchange}/{routing_key}")
        except Exception as e:
            logger.error(f"Ошибка публикации сообщения: {e}")
            raise

    # ─── Очереди ───────────────────────────────────────────────

    def declare_queue(self, queue_name: str, durable: bool = True):
        """Объявление очереди"""
        with self.channel() as ch:
            ch.queue_declare(queue=queue_name, durable=durable)

    def bind_queue(
        self,
        queue_name: str,
        exchange: str,
        routing_key: str,
        exchange_type: str = "direct",
    ):
        """Привязка очереди к exchange"""
        with self.channel() as ch:
            ch.exchange_declare(
                exchange=exchange, exchange_type=exchange_type, durable=True
            )
            ch.queue_declare(queue=queue_name, durable=True)
            ch.queue_bind(
                exchange=exchange, queue=queue_name, routing_key=routing_key
            )

    # ─── Потребление ───────────────────────────────────────────

    def consume_messages(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False,
    ):
        """Потребление сообщений из очереди (блокирующий вызов)"""

        def on_message(ch, method, properties, body):
            try:
                message = json.loads(body)
                callback(message)
                if not auto_ack:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Ошибка обработки сообщения: {e}")
                if not auto_ack:
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

        connection = None
        channel = None

        try:
            # Используем get_connection с retry
            connection = self.get_connection()
            channel = connection.channel()

            channel.queue_declare(queue=queue_name, durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(
                queue=queue_name,
                on_message_callback=on_message,
                auto_ack=auto_ack,
            )

            logger.info(f"Ожидание сообщений в очереди {queue_name}...")
            channel.start_consuming()
        except KeyboardInterrupt:
            logger.info(f"Остановка потребления из очереди {queue_name}")
            if channel and channel.is_open:
                channel.stop_consuming()
        except Exception as e:
            logger.error(f"Ошибка при потреблении из {queue_name}: {e}")
        finally:
            if channel and channel.is_open:
                try:
                    channel.close()
                except Exception:
                    pass
            if connection and connection.is_open:
                try:
                    connection.close()
                except Exception:
                    pass

    def start_consumer_thread(
        self,
        queue_name: str,
        callback: Callable,
        auto_ack: bool = False,
    ):
        """Запуск потребителя в отдельном потоке"""
        thread = threading.Thread(
            target=self.consume_messages,
            args=(queue_name, callback, auto_ack),
            daemon=True,
        )
        thread.start()
        return thread

    # ─── RPC ───────────────────────────────────────────────────

    def rpc_call(
        self,
        exchange: str,
        routing_key: str,
        message: Dict[Any, Any],
        response_queue: str,
        timeout: int = 5,
    ) -> Optional[Dict[Any, Any]]:
        """RPC вызов через RabbitMQ (Request-Reply паттерн)"""
        correlation_id = str(uuid.uuid4())
        message["correlation_id"] = correlation_id
        message["reply_to"] = response_queue

        response_received = {"data": None, "received": False}

        def on_response(ch, method, properties, body):
            if properties.correlation_id == correlation_id:
                response_received["data"] = json.loads(body)
                response_received["received"] = True
                ch.basic_ack(delivery_tag=method.delivery_tag)
                ch.stop_consuming()

        try:
            with self.channel() as ch:
                ch.queue_declare(
                    queue=response_queue, exclusive=True, auto_delete=True
                )
                ch.exchange_declare(
                    exchange=exchange, exchange_type="direct", durable=True
                )
                ch.basic_publish(
                    exchange=exchange,
                    routing_key=routing_key,
                    body=json.dumps(message),
                    properties=BasicProperties(
                        correlation_id=correlation_id,
                        reply_to=response_queue,
                    ),
                )
                ch.basic_consume(
                    queue=response_queue,
                    on_message_callback=on_response,
                    auto_ack=False,
                )

                start_time = time.time()
                while not response_received["received"]:
                    ch.connection.process_data_events(time_limit=0.1)
                    if time.time() - start_time > timeout:
                        return None

                return response_received["data"]
        except Exception as e:
            logger.error(f"Ошибка RPC вызова: {e}")
            return None