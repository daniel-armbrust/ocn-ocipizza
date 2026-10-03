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

    app_name: str = 'pizza-service'
    app_env: str = 'development'
    debug: bool = False

    # Persistência
    persistence_provider: str = 'nosql'

    # Oracle NoSQL
    nosql_table_name: str = 'pizzas'
    nosql_endpoint: str | None = None
    nosql_compartment_id: str | None = None

    # SQLAlchemy
    database_url: str | None = None

    # JWT
    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'oci-pizza'
    jwt_jwks_url: str = 'http://user-service:8000/.well-known/jwks.json'

    # Object Storage
    objectstorage_endpoint: str | None = None
    objectstorage_namespace: str | None = None
    objectstorage_bucket: str | None = None

    # Logging
    log_level: str = 'INFO'
    oci_log_id: str | None = None
    
@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()