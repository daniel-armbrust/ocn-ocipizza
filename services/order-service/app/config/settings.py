#
# config/settings.py
#

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações utilizadas pelo order-service.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'order-service'
    app_env: str = 'development'
    debug: bool = False

    # Persistência
    persistence_provider: str = 'nosql'

    # Oracle NoSQL
    nosql_table_name: str = 'orders'
    nosql_endpoint: str | None = None
    nosql_compartment_id: str | None = None
    oci_region: str | None = None

    # SQLAlchemy
    database_url: str | None = None

    # Timeout padrão utilizado nas chamadas HTTP realizadas 
    # aos microserviços.
    http_client_timeout: float = 10.0

    # JWT
    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'oci-pizza'
    jwt_jwks_url: str = 'http://user-service:8000/.well-known/jwks.json'

    # Credenciais utilizadas apenas no ambiente de desenvolvimento
    objectstorage_access_key: str | None = None
    objectstorage_secret_key: str | None = None

    # Logging
    log_level: str = 'INFO'
    oci_log_id: str | None = None
    
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
