#
# routes/pizza_routes.py
#

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import HTMLResponse

from app.dependencies.templates import templates

from app.messages.cart_messages import CART_MESSAGES
from app.messages.user_service_messages import USER_MESSAGES

from app.services.pizza_service import PizzaService, get_pizza_service

from app.utils.utils import normalize_optional_bool, normalize_optional_string

router = APIRouter()

#
# GET: /pizzas
#
@router.get(
    '/pizzas',
    response_class=HTMLResponse
)
async def list_all_pizzas(
    request: Request,
    code: str | None = None,
    category: str | None = None,
    available: str | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    pizza_service: PizzaService = Depends(get_pizza_service)
) -> HTMLResponse:
    """
    Renderiza a página contendo a lista de pizzas.

    Os dados são obtidos pelo frontend-service através do
    pizza-service.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        code: Código funcional opcional utilizado para identificar uma
            mensagem relacionada ao usuário.
        category: Categoria utilizada para filtrar as pizzas.
        available: Valor textual do filtro de disponibilidade. Valores
            vazios representam ausência do filtro.
        limit: Quantidade máxima de pizzas retornadas.
        offset: Quantidade de registros ignorados antes da consulta.
        pizza_service: Serviço responsável pela consulta do cardápio.

    Returns:
        Página HTML contendo as pizzas retornadas pelo pizza-service.
    """

    message = (
        USER_MESSAGES.get(code) or CART_MESSAGES.get(code)
        if code
        else None
    )

    # Normaliza os parâmetros opcionais recebidos pela URL, convertendo
    # valores vazios para `None` e o filtro de disponibilidade para booleano
    # antes de encaminhá-los ao pizza-service.

    normalized_category = normalize_optional_string(
        category
    )

    normalized_available = normalize_optional_bool(
        available
    )

    # Falhas HTTP e de comunicação são tratadas pelos handlers globais.
    pizzas = await pizza_service.get_all(
        category=normalized_category,
        available=normalized_available,
        limit=limit,
        offset=offset
    )

    # O pizza-service retorna somente o nome do objeto. A URL pública para a
    # imagem é fornecida pelo BFF, que mantém privado o Object Storage.
    pizza_items = pizzas.get('data', {}).get('pizzas', [])

    for pizza in pizza_items:
        pizza['image_url'] = f'/pizzas/{pizza["id"]}/image'

    return templates.TemplateResponse(
        request=request,
        name='pizzas/list.html',
        context={
            'pizzas': pizzas,
            'code': code,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'category': normalized_category,
            'available': normalized_available,
            'limit': limit,
            'offset': offset
        }
    )

#
# GET: /pizzas/{pizza_id}/image
#
@router.get(
    '/pizzas/{pizza_id}/image',
    response_class=Response
)
async def get_pizza_image(
    pizza_id: UUID,
    pizza_service: PizzaService = Depends(get_pizza_service)
) -> Response:
    """
    Encaminha ao navegador a imagem privada de uma pizza.

    Args:
        pizza_id: Identificador UUID da pizza consultada.
        pizza_service: Serviço responsável pela comunicação com o
            pizza-service.

    Returns:
        Resposta contendo os bytes da imagem e o tipo MIME informado pelo
        pizza-service.
    """

    image_data, content_type = await pizza_service.get_image(str(pizza_id))

    return Response(
        content=image_data,
        media_type=content_type
    )
