#
# routes/pizza_routes.py
#

from uuid import UUID

from fastapi import APIRouter, status, Depends, Query, Response
from fastapi.responses import JSONResponse

from app.services.pizza_service import PizzaService, get_pizza_service

from app.exceptions.pizza_exception import PizzaQueryError, PizzaNotFoundError

from app.schemas.pizza_schema import PizzaResponse, PizzaCategory

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
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: PizzaService = Depends(get_pizza_service)
) -> JSendSuccessResponse | JSONResponse:
    """
    Retorna as pizzas cadastradas de acordo com os filtros informados.

    Args:
        category: Categoria utilizada para filtrar as pizzas.
        available: Indica se o resultado deve ser filtrado
            pela disponibilidade.
        limit: Quantidade máxima de pizzas retornadas.
        offset: Quantidade de registros ignorados antes do retorno.
        service: Serviço responsável pelas operações relacionadas
            às pizzas.

    Returns:
        Resposta contendo a lista de pizzas encontradas.
    """

    try:
        pizzas = service.get_all(
            category=category,
            available=available,
            limit=limit,
            offset=offset
        )

        return success_response(
            data={
                'pizzas': [
                    PizzaResponse.from_model(pizza)
                    for pizza in pizzas
                ]
            }
        )

    except PizzaQueryError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
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
    Retorna uma pizza através de seu identificador.

    Args:
        pizza_id: Identificador UUID da pizza.
        service: Serviço responsável pelas operações relacionadas
            às pizzas.

    Returns:
        Resposta contendo os dados da pizza encontrada.
    """

    try:
        pizza = service.get_by_id(
            pizza_id=pizza_id
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
    except PizzaQueryError as ex:
        return fail_response(
            data={
                'message': str(ex)
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

#
# GET: /pizzas/{pizza_id}/image
#
@router.get(
    '/pizzas/{pizza_id}/image',
    status_code=status.HTTP_200_OK,
    response_model=None
)
def get_pizza_image(
    pizza_id: UUID,
    service: PizzaService = Depends(get_pizza_service)
) -> Response | JSONResponse:
    """
    Retorna a imagem associada à pizza informada.

    Args:
        pizza_id: Identificador UUID da pizza.
        service: Serviço responsável pelas operações relacionadas
            às pizzas.

    Returns:
        Conteúdo binário da imagem da pizza quando encontrada.
    """

    try:
        image_data, content_type = service.get_image(pizza_id)
    except PizzaNotFoundError:
        return fail_response(
            status_code=status.HTTP_404_NOT_FOUND,
            code='PIZZA_NOT_FOUND',
            message='Pizza not found.'
        )
    except PizzaQueryError:
        return fail_response(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code='PIZZA_IMAGE_QUERY_ERROR',
            message='Error retrieving pizza image.'
        )

    return Response(
        content=image_data,
        media_type=content_type
    )
