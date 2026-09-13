from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.clients.pizza_service import PizzaCatalogResult, PizzaServiceClient
from app.config.settings import Settings
from app.main import app


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def test_pizza_client_adds_object_storage_image_url() -> None:
    settings = Settings(
        environment="test",
        pizza_service_url="http://pizza-service:8000",
        pizza_image_base_url="http://localhost:9000/pizza-images",
        order_service_url="http://order-service:8000",
        payment_service_url="http://payment-service:8000",
        auth_service_url="http://auth-service:8000",
        user_service_url="http://user-service:8000",
        notification_service_url="http://notification-service:8000",
        chatbot_service_url="http://chatbot-service:8000",
        request_timeout=1.0,
    )
    pizza = PizzaServiceClient(settings)._with_image_url(
        {"id": 1, "image_name": "pizza-calabresa.jpg"}
    )

    assert (
        pizza["image_url"]
        == "http://localhost:9000/pizza-images/pizza-calabresa.jpg"
    )


@pytest.mark.anyio
async def test_index_renders_main_page(monkeypatch) -> None:
    async def fake_list_pizzas(self) -> PizzaCatalogResult:
        return PizzaCatalogResult(
            pizzas=[
                {
                    "id": 1,
                    "name": "Margherita",
                    "description": "Molho de tomate, queijo e manjericao",
                    "category": "tradicional",
                    "price": 39.9,
                    "image_url": "http://localhost:9000/pizza-images/margherita.jpg",
                    "available": True,
                },
            ],
        )

    monkeypatch.setattr(
        "app.routes.home_routes.PizzaServiceClient.list_pizzas",
        fake_list_pizzas,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "OCI Pizza" in response.text
    assert "Margherita" in response.text
    assert "http://localhost:9000/pizza-images/margherita.jpg" in response.text
    assert "Ver cardapio" in response.text


@pytest.mark.anyio
async def test_index_renders_catalog_error(monkeypatch) -> None:
    async def fake_list_pizzas(self) -> PizzaCatalogResult:
        return PizzaCatalogResult(
            pizzas=[],
            error_message="Nao foi possivel carregar o catalogo agora.",
        )

    monkeypatch.setattr(
        "app.routes.home_routes.PizzaServiceClient.list_pizzas",
        fake_list_pizzas,
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/")

    assert response.status_code == 200
    assert "Catalogo temporariamente indisponivel" in response.text
    assert "Nao foi possivel carregar o catalogo agora" in response.text
