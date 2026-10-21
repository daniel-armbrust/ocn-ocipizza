#
# routes/pizza_admin_routes.py
#

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Depends, File, UploadFile
from fastapi.responses import JSONResponse

from app.services.pizza_service import PizzaService, get_pizza_service

from app.dependencies.authentication import get_current_admin_id

from app.dependencies.pizza_form import (
    get_pizza_create_form,
    get_pizza_update_form
)

from app.exceptions.pizza_exception import (
    PizzaNotFoundError,
    PizzaCreationError,
    PizzaUpdateError,
    PizzaDeletionError
)

from app.schemas.pizza_schema import (
    PizzaCreateRequest,
    PizzaUpdateRequest,
    PizzaResponse
)

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import fail_response, success_response

router = APIRouter()

#
# POST: /admin/pizzas
#
@router.post(
    '/admin/pizzas',
    status_code=status.HTTP_201_CREATED,
    response_model=JSendSuccessResponse
)
def create_pizza(
    image: Annotated[UploadFile, File()],
    payload: PizzaCreateRequest = Depends(get_pizza_create_form),
    _: UUID = Depends(get_current_admin_id),
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Cria uma nova pizza e armazena sua respectiva imagem.

    Args:
        image: Arquivo de imagem associado à pizza.
        payload: Dados utilizados para criação da pizza.
        _: Identificador do usuário administrativo autenticado.
        service: Serviço responsável pelas operações relacionadas
            às pizzas.

    Returns:
        Resposta contendo os dados da pizza criada.
    """

    try:
        image_data = image.file.read()

        pizza = service.create(
            payload=payload,
            image_data=image_data,
            content_type=image.content_type
        )

        return success_response(
            data={
                'pizza': PizzaResponse.from_model(
                    pizza
                )
            }
        )
    except PizzaCreationError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

#
# PUT: /admin/pizzas/{pizza_id}
#
@router.put(
    '/admin/pizzas/{pizza_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_pizza(
    pizza_id: UUID,
    payload: PizzaUpdateRequest = Depends(get_pizza_update_form),
    image: Annotated[UploadFile | None, File()] = None,
    _: UUID = Depends(get_current_admin_id),
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Atualiza os dados de uma pizza e, quando informado,
    substitui sua imagem.

    Args:
        pizza_id: Identificador UUID da pizza.
        payload: Dados utilizados para atualização da pizza.
        image: Nova imagem associada à pizza, quando informada.
        _: Identificador do usuário administrativo autenticado.
        service: Serviço responsável pelas operações relacionadas
            às pizzas.

    Returns:
        Resposta contendo os dados da pizza atualizada.
    """

    try:
        image_data = None
        content_type = None

        if image is not None:
            image_data = image.file.read()
            content_type = image.content_type

        pizza = service.update(
            pizza_id=pizza_id,
            payload=payload,
            image_data=image_data,
            content_type=content_type
        )

        return success_response(
            data={
                'pizza': PizzaResponse.from_model(
                    pizza
                )
            }
        )
    except PizzaNotFoundError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    except PizzaUpdateError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

#
# DELETE: /admin/pizzas/{pizza_id}
#
@router.delete(
    '/admin/pizzas/{pizza_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def delete_pizza(
    pizza_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Remove uma pizza e sua respectiva imagem.

    Args:
        pizza_id: Identificador UUID da pizza.
        _: Identificador do usuário administrativo autenticado.
        service: Serviço responsável pelas operações relacionadas
            às pizzas.

    Returns:
        Resposta indicando que a pizza foi removida com sucesso.
    """

    try:
        service.delete(
            pizza_id=pizza_id
        )

        return success_response(
            data={
                'message': 'Pizza deleted successfully.'
            }
        )
    except PizzaNotFoundError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_404_NOT_FOUND
        )
    except PizzaDeletionError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )