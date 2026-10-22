#
# config/settings.py
#

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """
    Configurações utilizadas pelo notification-service.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'notification-service'
    app_env: str = 'development'
    debug: bool = False

    oci_region: str | None = 'sa-saopaulo-1'

    # URL base pública utilizada para construir links 
    # enviados aos usuários.
    site_url: str = 'https://www.ocipizza.com.br'

    # E-mail
    email_provider: Literal['smtp', 'oci'] = 'smtp'

    # Caminho do diretório que contém os templates utilizados
    # na construção dos e-mails de notificação.
    email_templates_path: str = str(
        APP_DIR / 'templates' / 'emails'
    )

    # OCI Email Delivery - OCID do compartment.
    oci_email_delivery_compartment_id: str | None = None

    # OCI Email Delivery - Nome apresentado como remetente 
    # das notificações.
    oci_email_sender_name: str = 'OCI Pizza'

    # SMTP
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_use_tls: bool = True
    smtp_email_sender: str = 'no-reply@ocipizza.com.br'

    # Mensageria
    messaging_provider: Literal['rabbitmq', 'oci_queue'] = 'oci_queue'
    queue_name: str = 'notifications-queue'

    # Intervalo, em segundos, entre as consultas à fila quando
    # nenhuma mensagem estiver disponível.
    notification_poll_interval: float = 5.0

    # Intervalo, em segundos, antes de uma nova tentativa após
    # ocorrer uma falha durante o consumo das notificações.
    notification_retry_interval: float = 10.0

    # RabbitMQ
    rabbitmq_host: str | None = None
    rabbitmq_port: int | None = None
    rabbitmq_username: str | None = None
    rabbitmq_password: str | None = None
    
    # OCI Queue
    oci_queue_id: str | None = None

    # Logging
    log_level: str = 'INFO'
    oci_log_id: str | None = None

    # Estratégia de autenticação utilizada para acessar os serviços
    # do OCI.
    oci_auth_mode: Literal[
        'config_file', 
        'instance_principal'
    ] = 'instance_principal'

    # Caminho do arquivo de configuração e profile usados para
    # autenticação nos serviços do OCI.
    oci_config_file: str | None = None
    oci_config_profile: str | None = None
    

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()