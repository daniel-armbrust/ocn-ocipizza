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

    # Define o ambiente de execução da aplicação.
    # Por padrão, utiliza "production" para priorizar 
    # configurações de segurança.
    app_env: Literal[
        'development', 
        'production'
    ] = 'production'

    # Região opcional para desenvolvimento local. Em execução na OCI, o
    # Instance Principal identifica automaticamente a região do ambiente.
    oci_region: str | None = None

    # Persistência
    # TODO: Implementar suporte ao OCI NoSQL neste serviço.
    persistence_provider: Literal['nosql', 'sqlalchemy'] = 'sqlalchemy'

    # SQLAlchemy
    #   URL de conexão com o MySQL primário, utilizada para escrita
    #   e leituras que exigem consistência imediata.
    database_write_url: str | None = None

    # SQLAlchemy
    #   URL de conexão com o MySQL regional, utilizada para leituras
    #   que toleram consistência eventual.
    database_read_url: str | None = None

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

    # Provedor da chave privada utilizada para assinar JWTs.
    jwt_key_provider: Literal['file', 'oci'] = 'file'

    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'ocipizza'
    jwt_access_token_expiration_minutes: int = 15

    # Caminhos das chaves JWT utilizadas quando JWT_KEY_PROVIDER for "file".
    jwt_private_key_path: str = '/run/secrets/jwt_private_key.pem'
    jwt_public_key_path: str = '/run/secrets/jwt_public_key.pem'

    # OCID do Secret no OCI Vault que armazena a chave privada JWT.
    jwt_private_key_secret_id: str | None = None

    # OCID do Secret no OCI Vault que armazena a chave pública JWT.
    jwt_public_key_secret_id: str | None = None

    # Refresh token
    refresh_token_expiration_days: int = 30

    # Logging
    debug: bool = False
    log_level: str = 'INFO'
    oci_log_id: str | None = None

    # Define o método de autenticação utilizado para acessar os serviços OCI:
    #   None: desabilita a autenticação OCI, permitindo o uso de serviços locais.
    #   "config_file": utiliza as credenciais configuradas na máquina de desenvolvimento.
    #   "instance_principal": utiliza a identidade de uma instância Compute.
    #   "resource_principal": utiliza a identidade do recurso OCI, como Container Instances.
    #   "workload_identity": utiliza a identidade do workload executado no OKE.
    oci_auth_mode: Literal[
        'config_file',
        'instance_principal',
        'resource_principal',
        'workload_identity'
    ] | None = None

    # Caminho do arquivo de configuração e profile usados para
    # autenticação nos serviços do OCI.
    oci_config_file: str | None = None
    oci_config_profile: str = 'DEFAULT'


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
