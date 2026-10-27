#
# config/settings.py
#

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações utilizadas pelo delivery-service.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'delivery-service'
    app_env: str = 'development'
    debug: bool = False

    # Região do OCI onde a aplicação será executada.
    oci_region: str | None

    # Persistência
    persistence_provider: Literal['nosql', 'sqlalchemy'] = 'nosql'
    
    # Oracle NoSQL
    nosql_provider: Literal['local', 'oci'] = 'local'
    nosql_table_name: str = 'delivery_areas'
    nosql_endpoint: str | None = None
    nosql_compartment_id: str | None = None

    # SQLAlchemy
    database_url: str | None = None

    # Timeout padrão utilizado nas chamadas HTTP realizadas 
    # aos microserviços.
    http_client_timeout: float = 10.0
    
    # JWT
    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'ocipizza'
    jwt_jwks_url: str

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
