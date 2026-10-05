#
# routes/pizza_routes.py
#

from uuid import UUID
from typing import Annotated

from fastapi import APIRouter, status, Depends, File, Query, UploadFile
from fastapi.responses import JSONResponse

from app.services.pizza_service import PizzaService, get_pizza_service

from app.dependencies.authentication import get_current_admin_id
from app.dependencies.pizza_form import (
    get_pizza_create_form,
    get_pizza_update_form
)

from app.exceptions.pizza_exception import (
    PizzaQueryError,
    PizzaNotFoundError,
    PizzaCreationError,
    PizzaUpdateError,
    PizzaDeletionError
)

from app.schemas.pizza_schema import (
    PizzaCreateRequest,
    PizzaUpdateRequest,
    PizzaResponse,
    PizzaCategory
)

from app.schemas.jsend_schema import JSendSuccessResponse
from app.responses.jsend import fail_response, success_response

router = APIRouter()

#
# GET: /pizzas
#
@router.get(
    '/pizzas',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def list_pizzas(
    category: PizzaCategory | None = None,
    available: bool | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna as pizzas cadastradas de acordo com os filtros informados.

    Args:
        category: Categoria utilizada para filtrar as pizzas.
        available: Filtra pizzas de acordo com sua disponibilidade.
        limit: Quantidade máxima de pizzas retornadas.
        offset: Quantidade de registros ignorados antes do retorno.
        service: Serviço responsável pelos casos de uso relacionados
            às pizzas.

    Returns:
        Resposta no padrão JSend contendo as pizzas encontradas.
    """

    try:
        pizzas = service.get_all(
            category=category,
            available=available,
            limit=limit,
            offset=offset    
        )
    except PizzaQueryError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PIZZA_QUERY_ERROR',
            'Error retrieving pizzas.'
        )

    return success_response(
        {
            'pizzas': [
                PizzaResponse.from_model(
                    pizza,
                    image_url=image_url
                ).model_dump(mode='json')
                for pizza, image_url in pizzas
            ]
        }
    )

#
# GET: /pizzas/{pizza_id}
#
@router.get(
    '/pizzas/{pizza_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_pizza(
    pizza_id: UUID,
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna os dados de uma pizza específica.

    Args:
        pizza_id: Identificador UUID da pizza que será consultada.
        service: Serviço responsável pelos casos de uso relacionados
            às pizzas.

    Returns:
        Resposta no padrão JSend contendo os dados da pizza encontrada.
        Caso a pizza não exista, retorna uma resposta JSend com status
        HTTP 404. Em caso de falha durante a consulta, retorna uma
        resposta JSend com status HTTP 500.
    """

    try:
        pizza, image_url = service.get_by_id(pizza_id=pizza_id)
    except PizzaNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'PIZZA_NOT_FOUND',
            'Pizza not found.'
        )
    except PizzaQueryError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PIZZA_QUERY_ERROR',
            'Error retrieving pizza.'
        )
    
    return success_response(
        {
            'pizza': PizzaResponse.from_model(
                pizza,
                image_url=image_url
            ).model_dump(mode='json')
        }
    )

#
# POST: /pizzas
#
@router.post(
    '/pizzas',
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
    Cria uma nova pizza.

    Esta operação é restrita a usuários com privilégios
    administrativos.

    Args:
        payload: Dados necessários para criação da pizza.
        image: Arquivo de imagem associado à pizza.
        service: Serviço responsável pelos casos de uso relacionados
            às pizzas.

    Returns:
        Resposta no padrão JSend contendo os dados da pizza criada.
        Em caso de falha durante a criação, retorna uma resposta
        JSend com status HTTP 500.
    """

    if not image.content_type or not image.content_type.startswith('image/'):
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'PIZZA_INVALID_IMAGE_CONTENT_TYPE',
            'The uploaded file must be an image.',
            field='image'
        )

    image_data = image.file.read()

    if not image_data:
        return fail_response(
            status.HTTP_400_BAD_REQUEST,
            'PIZZA_EMPTY_IMAGE',
            'The uploaded image must not be empty.',
            field='image'
        )

    try:
        pizza, image_url = service.create(
            payload=payload,
            image_data=image_data,
            content_type=image.content_type
        )
    except PizzaCreationError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PIZZA_CREATION_ERROR',
            'Error creating pizza.'
        )

    return success_response(
        {
            'pizza': PizzaResponse.from_model(
                pizza,
                image_url=image_url
            ).model_dump(mode='json')
        }
    )

#
# PUT: /pizzas/{pizza_id}
#
@router.put(
    '/pizzas/{pizza_id}',
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
    Atualiza os dados de uma pizza.

    Esta operação é restrita a usuários com privilégios
    administrativos.

    Args:
        pizza_id: Identificador UUID da pizza que será atualizada.
        payload: Dados permitidos para atualização da pizza.
        image: Novo arquivo de imagem, quando a imagem também for atualizada.
        service: Serviço responsável pelos casos de uso relacionados
            às pizzas.

    Returns:
        Resposta no padrão JSend contendo os dados atualizados da pizza.
        Caso a pizza não exista, retorna uma resposta JSend com status
        HTTP 404. Em caso de falha durante a atualização, retorna uma
        resposta JSend com status HTTP 500.
    """

    image_data = None
    content_type = None

    if image is not None:
        if not image.content_type or not image.content_type.startswith('image/'):
            return fail_response(
                status.HTTP_400_BAD_REQUEST,
                'PIZZA_INVALID_IMAGE_CONTENT_TYPE',
                'The uploaded file must be an image.',
                field='image'
            )

        image_data = image.file.read()

        if not image_data:
            return fail_response(
                status.HTTP_400_BAD_REQUEST,
                'PIZZA_EMPTY_IMAGE',
                'The uploaded image must not be empty.',
                field='image'
            )

        content_type = image.content_type

    try:
        pizza, image_url = service.update(
            pizza_id,
            payload,
            image_data=image_data,
            content_type=content_type
        )
    except PizzaNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'PIZZA_NOT_FOUND',
            'Pizza not found.'
        )
    except PizzaUpdateError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PIZZA_UPDATE_ERROR',
            'Error updating pizza.'
        )

    return success_response(
        {
            'pizza': PizzaResponse.from_model(
                pizza,
                image_url=image_url
            ).model_dump(mode='json')
        }
    )

#
# DELETE: /pizzas/{pizza_id}
#
@router.delete(
    '/pizzas/{pizza_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def delete_pizza(
    pizza_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Remove uma pizza.

    Esta operação é restrita a usuários com privilégios
    administrativos.

    Args:
        pizza_id: Identificador UUID da pizza que será removida.
        service: Serviço responsável pelos casos de uso relacionados
            às pizzas.

    Returns:
        Resposta no padrão JSend indicando o resultado da operação.
        Caso a pizza não exista, retorna uma resposta JSend com status
        HTTP 404. Em caso de falha durante a remoção, retorna uma
        resposta JSend com status HTTP 500.
    """

    try:
        service.delete(pizza_id=pizza_id)
    except PizzaNotFoundError:
        return fail_response(
            status.HTTP_404_NOT_FOUND,
            'PIZZA_NOT_FOUND',
            'Pizza not found.'
        )
    except PizzaDeletionError:
        return fail_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'PIZZA_DELETION_ERROR',
            'Error deleting pizza.'
        )

    return success_response(
        {
            'message': 'Pizza deleted successfully.',
        }
    )
