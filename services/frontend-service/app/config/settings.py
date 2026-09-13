from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    environment: str
    pizza_service_url: str
    pizza_image_base_url: str
    order_service_url: str
    payment_service_url: str
    auth_service_url: str
    user_service_url: str
    notification_service_url: str
    chatbot_service_url: str
    request_timeout: float


def _getenv(name: str, default: str) -> str:
    value = os.getenv(name)

    if value is None or value == "":
        return default

    return value


@lru_cache
def get_settings() -> Settings:
    timeout = _getenv("FRONTEND_REQUEST_TIMEOUT", "2.0")

    return Settings(
        environment=_getenv("ENVIRONMENT", "development"),
        request_timeout=float(timeout),

        pizza_service_url=_getenv("PIZZA_SERVICE_URL", "http://pizza-service:8000"),
        pizza_image_base_url=_getenv("PIZZA_IMAGE_BASE_URL", "http://localhost:9000/pizza-images"),
        order_service_url=_getenv("ORDER_SERVICE_URL", "http://order-service:8000"),
        payment_service_url=_getenv("PAYMENT_SERVICE_URL","http://payment-service:8000"),
        auth_service_url=_getenv("AUTH_SERVICE_URL", "http://auth-service:8000"),
        user_service_url=_getenv("USER_SERVICE_URL", "http://user-service:8000"),
        notification_service_url=_getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8000"),
        chatbot_service_url=_getenv("CHATBOT_SERVICE_URL", "http://chatbot-service:8000"),
    )
