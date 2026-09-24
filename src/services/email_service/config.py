import os

from dotenv import load_dotenv

config_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(config_dir, '.env')
load_dotenv(dotenv_path)


class Settings:

    RABBIT_MQ_LOGIN: str = os.environ.get('RABBIT_MQ_LOGIN')
    RABBIT_MQ_PASSWORD: str = os.environ.get('RABBIT_MQ_PASSWORD')
    RABBIT_MQ_PORT: str = os.environ.get('RABBIT_MQ_PORT')
    RABBIT_MQ_HOST: str = os.environ.get('RABBIT_MQ_HOST')
    rabbitmq_url: str = f"amqp://{RABBIT_MQ_LOGIN}:{RABBIT_MQ_PASSWORD}@{RABBIT_MQ_HOST}:{RABBIT_MQ_PORT}/"

settings = Settings()