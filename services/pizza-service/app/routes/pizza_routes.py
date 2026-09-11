from fastapi import APIRouter, Depends, Path, status
from fastapi.responses import JSONResponse

from app.dependencies.auth import require_admin
from app.dependencies.nosql import get_pizza_service
from app.schemas.pizza_schema import PizzaCreateRequest, PizzaUpdateRequest
from app.services.pizza_service import PizzaNotFoundError, PizzaService

router = APIRouter(prefix="/pizzas", tags=["Pizzas"])


@router.get("")
def list_pizzas(
    service: PizzaService = Depends(get_pizza_service),
) -> dict:
    pizzas = service.list_available_pizzas()
    return {
        "status": "success",
        "data": {"pizzas": [pizza.model_dump(mode="json") for pizza in pizzas]},
    }


@router.get("/{id}")
def get_pizza(
    pizza_id: int = Path(alias="id", ge=1),
    service: PizzaService = Depends(get_pizza_service),
) -> dict:
    try:
        pizza = service.get_pizza(pizza_id)
    except PizzaNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "fail",
                "data": {
                    "code": "PIZZA_NOT_FOUND",
                    "field": "id",
                    "message": "Pizza not found",
                },
            },
        )

    return {
        "status": "success",
        "data": {"pizza": pizza.model_dump(mode="json")},
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def create_pizza(
    payload: PizzaCreateRequest,
    service: PizzaService = Depends(get_pizza_service),
    _: None = Depends(require_admin),
) -> dict:
    pizza = service.create_pizza(payload)
    return {
        "status": "success",
        "data": {"pizza": pizza.model_dump(mode="json")},
    }


@router.patch("/{id}")
def update_pizza(
    payload: PizzaUpdateRequest,
    pizza_id: int = Path(alias="id", ge=1),
    service: PizzaService = Depends(get_pizza_service),
    _: None = Depends(require_admin),
) -> dict:
    try:
        pizza = service.update_pizza(pizza_id, payload)
    except PizzaNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "fail",
                "data": {
                    "code": "PIZZA_NOT_FOUND",
                    "field": "id",
                    "message": "Pizza not found",
                },
            },
        )

    return {
        "status": "success",
        "data": {"pizza": pizza.model_dump(mode="json")},
    }


@router.delete("/{id}")
def delete_pizza(
    pizza_id: int = Path(alias="id", ge=1),
    service: PizzaService = Depends(get_pizza_service),
    _: None = Depends(require_admin),
) -> dict:
    try:
        service.delete_pizza(pizza_id)
    except PizzaNotFoundError:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "status": "fail",
                "data": {
                    "code": "PIZZA_NOT_FOUND",
                    "field": "id",
                    "message": "Pizza not found",
                },
            },
        )

    return {"status": "success", "data": None}
