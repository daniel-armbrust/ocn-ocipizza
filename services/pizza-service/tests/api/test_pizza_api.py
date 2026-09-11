from fastapi.testclient import TestClient

from app.dependencies.nosql import get_pizza_repository
from app.main import app
from app.repositories.pizza_repository import InMemoryPizzaRepository


client = TestClient(app)


def setup_function():
    get_pizza_repository.cache_clear()
    app.dependency_overrides[get_pizza_repository] = InMemoryPizzaRepository


def teardown_function():
    app.dependency_overrides.clear()


def test_get_pizzas_returns_jsend_list():
    response = client.get("/pizzas")

    assert response.status_code == 200
    assert response.json() == {
        "status": "success",
        "data": {"pizzas": []},
    }


def test_post_pizza_requires_admin_token():
    response = client.post(
        "/pizzas",
        json={
            "name": "Margherita",
            "category": "tradicional",
            "price": 39.9,
        },
    )

    assert response.status_code == 401
    assert response.json()["status"] == "error"


def test_post_and_get_pizza():
    created = client.post(
        "/pizzas",
        headers={"Authorization": "Bearer admin-token"},
        json={
            "name": "Margherita",
            "description": "Molho de tomate, queijo e manjericão",
            "category": "tradicional",
            "price": 39.9,
            "image_name": "margherita.jpg",
        },
    )

    pizza_id = created.json()["data"]["pizza"]["id"]
    found = client.get(f"/pizzas/{pizza_id}")

    assert created.status_code == 201
    assert found.status_code == 200
    assert found.json()["data"]["pizza"]["name"] == "Margherita"


def test_post_pizza_rejects_invalid_category():
    response = client.post(
        "/pizzas",
        headers={"Authorization": "Bearer admin-token"},
        json={
            "name": "Invalida",
            "category": "salgada",
            "price": 39.9,
        },
    )

    assert response.status_code == 400
    assert response.json()["status"] == "fail"


def test_delete_pizza_returns_jsend_success():
    created = client.post(
        "/pizzas",
        headers={"Authorization": "Bearer admin-token"},
        json={
            "name": "Chocolate",
            "category": "doce",
            "price": 45.0,
        },
    )
    pizza_id = created.json()["data"]["pizza"]["id"]

    deleted = client.delete(
        f"/pizzas/{pizza_id}",
        headers={"Authorization": "Bearer admin-token"},
    )

    assert deleted.status_code == 200
    assert deleted.json() == {"status": "success", "data": None}
