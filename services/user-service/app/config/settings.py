#
# config/settings.py
#

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações utilizadas pelo user-service.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        env_ignore_empty=True,
        extra='ignore',
    )

    app_name: str = 'user-service'
    app_env: str = 'development'
    debug: bool = False

    # Região do OCI onde a aplicação será executada.
    oci_region: str | None

    # Persistência
    persistence_provider: Literal['nosql', 'sqlalchemy'] = 'sqlalchemy'

    # SQLAlchemy
    database_url: str | None = None

    # Mensageria
    messaging_provider: Literal['rabbitmq', 'oci_queue'] = 'oci_queue'
    queue_name: str = 'notifications-queue'

    # RabbitMQ
    rabbitmq_host: str | None = None
    rabbitmq_port: int | None = None
    rabbitmq_username: str | None = None
    rabbitmq_password: str | None = None
    
    # OCI Queue
    oci_queue_id: str | None = None

    # JWT
    jwt_key_provider: str = 'local'
    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'ocipizza'
    jwt_access_token_expiration_minutes: int = 15
   
    jwt_private_key_path: str = '/run/secrets/jwt_private_key.pem'
    jwt_public_key_path: str = '/run/secrets/jwt_public_key.pem'

    jwt_private_key_secret_id: str | None = None

    # Refresh token
    refresh_token_expiration_days: int = 30

    # Logging
    log_level: str = 'INFO'
    oci_log_id: str | None = None

    # Define o método de autenticação utilizado para acessar os
    # serviços OCI:
    #   None desabilita a autenticação OCI, permitindo o uso de
    #       serviços locais.
    #   "config_file" utiliza as credenciais configuradas na máquina
    #       de desenvolvimento.
    #   "instance_principal" utiliza a identidade da instância Compute
    #       no OCI.
    oci_auth_mode: Literal[
        'config_file',
        'instance_principal',
    ] | None = None

    # Caminho do arquivo de configuração e profile usados para
    # autenticação nos serviços do OCI.
    oci_config_file: str | None = None
    oci_config_profile: str | None = None


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
