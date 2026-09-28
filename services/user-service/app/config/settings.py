#
# config/settings.py
#

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'user-service'
    app_env: str = 'development'
    debug: bool = False

    # Persistência
    persistence_provider: str
    database_url: str

    # Mensageria
    messaging_provider: str

    # RabbitMQ
    rabbitmq_host: str | None = None
    rabbitmq_port: int | None = None
    rabbitmq_username: str | None = None
    rabbitmq_password: str | None = None
    rabbitmq_queue_name: str | None = None

    # OCI Queue
    oci_queue_id: str | None = None
    oci_queue_messages_endpoint: str | None = None
    oci_region: str | None = None

    # JWT
    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'oci-pizza'


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()