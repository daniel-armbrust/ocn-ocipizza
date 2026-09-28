from fastapi import APIRouter, Depends, Path, status

from app.dependencies.auth import require_admin
from app.dependencies.nosql import get_pizza_service
from app.routes.responses import fail_response
from app.schemas.pizza_schema import PizzaCreateRequest, PizzaUpdateRequest
from app.services.pizza_service import PizzaNotFoundError, PizzaService

router = APIRouter(prefix="/pizzas", tags=["Pizzas"])


@router.get("")
def list_pizzas(
    service: PizzaService = Depends(get_pizza_service),
) -> dict:
    """
    Lista pizzas disponíveis no catálogo.

    Args:
        service: Serviço de domínio usado para consultar pizzas.

    Returns:
        Dicionário JSend contendo a lista de pizzas disponíveis.
    """

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
    """
    Consulta uma pizza pelo identificador informado na rota.

    Args:
        pizza_id: Identificador da pizza extraído do caminho da requisição.
        service: Serviço de domínio usado para consultar pizzas.

    Returns:
        Dicionário JSend com os dados da pizza ou falha de não encontrado.
    """

    try:
        pizza = service.get_pizza(pizza_id)
    except PizzaNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            "PIZZA_NOT_FOUND",
            "Pizza not found",
            field="id",
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
    """
    Cadastra uma nova pizza em operação administrativa.

    Args:
        payload: Dados validados para criação da pizza.
        service: Serviço de domínio usado para criar pizzas.
        _: Dependência que valida permissão administrativa.

    Returns:
        Dicionário JSend contendo a pizza criada.
    """

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
    """
    Atualiza dados de uma pizza existente em operação administrativa.

    Args:
        payload: Campos validados enviados para atualização.
        pizza_id: Identificador da pizza extraído do caminho da requisição.
        service: Serviço de domínio usado para atualizar pizzas.
        _: Dependência que valida permissão administrativa.

    Returns:
        Dicionário JSend com a pizza atualizada ou falha de não encontrado.
    """

    try:
        pizza = service.update_pizza(pizza_id, payload)
    except PizzaNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            "PIZZA_NOT_FOUND",
            "Pizza not found",
            field="id",
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
    """
    Remove uma pizza do catálogo em operação administrativa.

    Args:
        pizza_id: Identificador da pizza extraído do caminho da requisição.
        service: Serviço de domínio usado para remover pizzas.
        _: Dependência que valida permissão administrativa.

    Returns:
        Dicionário JSend com sucesso ou falha de não encontrado.
    """

    try:
        service.delete_pizza(pizza_id)
    except PizzaNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            "PIZZA_NOT_FOUND",
            "Pizza not found",
            field="id",
        )

    return {"status": "success", "data": None}
