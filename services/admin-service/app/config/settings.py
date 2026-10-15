#
# config/settings.py
#

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações utilizadas pelo admin-service.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'admin-service'
    app_env: str = 'development'
    debug: bool = False

    oci_region: str = 'sa-saopaulo-1'

    # Nome do cookie utilizado para identificar a sessão 
    # administrativa. 
    session_cookie_name: str = 'admocpssid'

    # Tempo de vida da sessão administrativa, em segundos. 
    session_ttl: int = 3600

    # Chaves utilizadas pelas sessões internas e pela proteção CSRF
    # mantidas pelo frontend-service.
    session_secret_key: str
    csrf_secret_key: str

    # Persistência
    persistence_provider: str = 'redis'

    # Redis
    redis_endpoint: str
    redis_user: str | None = None
    redis_password: str | None = None

    # URL dos serviços acessados pelo admin-service.
    pizza_service_url: str
    user_service_url: str
    delivery_service_url: str
    order_service_url: str
    notification_service_url: str

    # Timeout padrão utilizado nas chamadas HTTP realizadas 
    # aos microserviços.
    http_client_timeout: float = 10.0

    # JWT
    jwt_issuer: str = 'user-service'
    jwt_audience: str = 'ocipizza'
    jwt_jwks_url: str

    # Object Storage
    objectstorage_endpoint: str
    objectstorage_namespace: str | None = None 
    
    # Credenciais do Object Storage utilizadas apenas no ambiente 
    # de desenvolvimento.
    objectstorage_access_key: str | None = None
    objectstorage_secret_key: str | None = None

    # Object Storage Bucket para as imagens das pizzas.
    pizza_images_objectstorage_bucket: str

    # Logging
    log_level: str = 'INFO'
    oci_log_id: str | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()