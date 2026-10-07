#
# routes/pizza_routes.py
#

import httpx

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse

from app.clients.pizza_client import PizzaClient, get_pizza_client

from app.dependencies.templates import templates

from app.messages.pizza_messages import PIZZA_MESSAGES
from app.messages.user_messages import USER_MESSAGES

router = APIRouter()

#
# GET: /pizzas
#
@router.get(
    '/pizzas',
    response_class=HTMLResponse,
)
async def list_all_pizzas(
    request: Request,
    code: str | None = None,
    category: str | None = None,
    available: bool | None = None,
    limit: int = Query(default=10, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    pizza_client: PizzaClient = Depends(get_pizza_client)
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
        available: Indica se devem ser retornadas pizzas disponíveis
            ou indisponíveis.
        limit: Quantidade máxima de pizzas retornadas.
        offset: Quantidade de registros ignorados antes da consulta.
        pizza_client: Cliente utilizado para comunicação com o
            pizza-service.

    Returns:
        Página HTML contendo as pizzas retornadas pelo pizza-service.
    """

    user_message = USER_MESSAGES.get(code) if code else None

    try:
        pizzas = await pizza_client.get_all(
            category=category,
            available=available,
            limit=limit,
            offset=offset
        )
    except httpx.HTTPStatusError as ex:
        payload = ex.response.json()

        message = PIZZA_MESSAGES.get(
            payload.get('data', {}).get('code'),
            {
                'message': 'Não foi possível processar a solicitação da pizza.',
                'type': 'error'
            }
        )

        return templates.TemplateResponse(
            request=request,
            name='pizzas/list.html',
            context={
                'message': message['message'],
                'type': message['type'],
                'pizzas': {},
                'category': category,
                'available': available,
                'limit': limit,
                'offset': offset
            },
            status_code=ex.response.status_code
        )
    except httpx.RequestError:
        return templates.TemplateResponse(
            request=request,
            name='errors/503.html',
            context={
                'message': (
                    'O serviço de pizzas está temporariamente indisponível.'
                )
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return templates.TemplateResponse(
        request=request,
        name='pizzas/list.html',
        context={
            'pizzas': pizzas,
            'code': code,
            'message': user_message['message'] if user_message else None,
            'type': user_message['type'] if user_message else None,
            'category': category,
            'available': available,
            'limit': limit,
            'offset': offset
        }
    )
