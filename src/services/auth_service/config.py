import os

from dotenv import load_dotenv

config_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(config_dir, '.env')
load_dotenv(dotenv_path)


class Settings:
    MODE: str = os.environ.get('MODE')

    DB_HOST: str = os.environ.get('DB_HOST')
    DB_PORT: int = os.environ.get('DB_PORT')
    DB_USER: str = os.environ.get('DB_USER')
    DB_PASS: str = os.environ.get('DB_PASS')
    DB_NAME: str = os.environ.get('DB_NAME')
    secret_key: str = os.environ.get('SECRET_KEY')
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    JWT_ACCESS_COOKIE_NAME: str = os.environ.get('JWT_ACCESS_COOKIE_NAME')
    RABBIT_MQ_LOGIN: str = os.environ.get('RABBIT_MQ_LOGIN')
    RABBIT_MQ_PASSWORD: str = os.environ.get('RABBIT_MQ_PASSWORD')
    RABBIT_MQ_PORT: str = os.environ.get('RABBIT_MQ_PORT')
    RABBIT_MQ_HOST: str = os.environ.get('RABBIT_MQ_HOST')
    DB_URL: str = f'postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    rabbitmq_url: str = f"amqp://{RABBIT_MQ_LOGIN}:{RABBIT_MQ_PASSWORD}@{RABBIT_MQ_HOST}:{RABBIT_MQ_PORT}/"

settings = Settings()