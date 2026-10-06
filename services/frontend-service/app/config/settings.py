#
# config/settings.py
#

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Configurações utilizadas pelo frontend-service.
    """

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

    app_name: str = 'frontend-service'
    app_env: str = 'development'
    debug: bool = False

    # Persistência
    persistence_provider: str = 'redis'

    # Redis
    redis_endpoint: str | None = None

    # Nome do cookie utilizado para identificar o cookie de
    # sessão.
    session_cookie_name: str = 'ocpssid'

    # URL dos serviços acessados pelo frontend-service.
    pizza_service_url: str
    user_service_url: str

    # Timeout padrão utilizado nas chamadas HTTP realizadas 
    # aos microserviços.
    http_client_timeout: float = 10.0

    # Timeout utilizado nas chamadas ao chatbot-service, que 
    # podem demandar mais tempo devido ao processamento de solicitações 
    # por modelos de IA.
    chatbot_client_timeout: float = 60.0

    # Logging
    log_level: str = 'INFO'
    oci_log_id: str | None = None

@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
