#
# routes/kitchen_order_routes.py
#

import logging
from uuid import UUID

import httpx

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.forms.order_forms import OrderStatusForm
from app.messages.order_service_messages import ORDER_MESSAGES
from app.messages.user_service_messages import USER_MESSAGES

from app.dependencies.authentication import get_kitchen_authenticated_session
from app.dependencies.templates import templates

from app.services.order_service import OrderService, get_order_service

router = APIRouter()
logger = logging.getLogger(__name__)

#
# GET: /kitchen/orders
#
@router.get(
    '/kitchen/orders',
    response_class=HTMLResponse
)
async def show_kitchen_orders(
    request: Request,
    code: str | None = None,
    search: str | None = None,
    selected_status: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: dict = Depends(get_kitchen_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Exibe a página principal de pedidos da cozinha.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código opcional da mensagem apresentada no modal.
        search: Número de pedido utilizado na consulta.
        selected_status: Status utilizado para filtrar os pedidos.
        limit: Quantidade máxima de pedidos exibidos por página.
        offset: Quantidade de pedidos ignorados antes da página atual.
        session: Sessão da cozinha validada pela dependência da rota.
        order_service: Serviço responsável pelas operações de pedidos.

    Returns:
        Página HTML contendo a consulta operacional dos pedidos.
    """

    message = None

    if code:
        message = (
            ORDER_MESSAGES.get(code) or
            USER_MESSAGES.get(code)
        )

    paginated_orders = await order_service.get_all(
        access_token=session['access_token'],
        status=selected_status,

        # Busca um item além do limite apenas para detectar se existe uma
        # próxima página; esse item adicional não é exibido.
        # TODO: Usar o total informado pelo order-service quando o contrato
        # da API passar a fornecer metadados de paginação.
        limit=limit + 1,
        offset=offset
    )

    has_next_page = len(paginated_orders) > limit
    orders = paginated_orders[:limit]

    received_count = sum(
        order.get('status') == 'RECEIVED'
        for order in orders
    )

    preparing_count = sum(
        order.get('status') == 'PREPARING'
        for order in orders
    )
    
    ready_count = sum(
        order.get('status') == 'READY'
        for order in orders
    )

    return templates.TemplateResponse(
        request=request,
        name='kitchen/orders.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'orders': orders,
            'total_orders': len(orders),
            'received_count': received_count,
            'preparing_count': preparing_count,
            'ready_count': ready_count,
            'search': search,
            'selected_status': selected_status,
            'limit': limit,
            'offset': offset,
            'current_page': (offset // limit) + 1,
            'previous_offset': max(0, offset - limit),
            'next_offset': offset + limit,
            'has_previous_page': offset > 0,
            'has_next_page': has_next_page
        }
    )

#
# GET: /kitchen/orders/{order_id}
#
@router.get(
    '/kitchen/orders/{order_id}',
    response_class=HTMLResponse
)
async def show_kitchen_order(
    request: Request,
    order_id: UUID,
    code: str | None = None,
    session: dict = Depends(get_kitchen_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Exibe os detalhes operacionais de um pedido para a cozinha.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        order_id: Identificador UUID do pedido consultado.
        code: Código opcional da mensagem apresentada no modal.
        session: Sessão da cozinha validada pela dependência da rota.
        order_service: Serviço responsável pelas operações de pedidos.

    Returns:
        Página HTML contendo os detalhes operacionais do pedido.
    """

    message = None

    if code:
        message = (
            ORDER_MESSAGES.get(code) or
            USER_MESSAGES.get(code)
        )

    # Obtém todos os dados do pedido que serão exibidos na página.
    order = await order_service.get_by_id(
        access_token=session['access_token'],
        order_id=order_id
    )

    # Obtém o total global de pedidos pendentes exibido no menu lateral.
    order_summary = await order_service.get_summary(
        access_token=session['access_token']
    )

    return templates.TemplateResponse(
        request=request,
        name='kitchen/order.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'order': order,
            'kitchen_total': order_summary['pending_orders']
        }
    )

#
# POST: /kitchen/orders/{order_id}/status
#
@router.post('/kitchen/orders/{order_id}/status')
@csrf_protect
async def update_kitchen_order_status(
    request: Request,
    order_id: UUID,
    session: dict = Depends(get_kitchen_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Atualiza o status operacional de um pedido pela área da cozinha.

    Args:
        request: Requisição HTTP contendo o status enviado pelo formulário.
        order_id: Identificador UUID do pedido atualizado.
        session: Sessão da cozinha validada pela dependência da rota.
        order_service: Serviço responsável pela comunicação com os pedidos.

    Returns:
        Redirecionamento para os detalhes do pedido com o resultado da operação.
    """

    form = OrderStatusForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=(
                f'/kitchen/orders/{order_id}?'
                'code=ORDER_SERVICE_VALIDATION_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    new_status = form.status.data

    if new_status not in {'PREPARING', 'READY'}:
        return RedirectResponse(
            url=(
                f'/kitchen/orders/{order_id}?'
                'code=ORDER_SERVICE_VALIDATION_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await order_service.update_status(
            access_token=session['access_token'],
            order_id=order_id,
            status=new_status
        )
    except httpx.HTTPStatusError as ex:
        logger.warning(
            'Order-service rejected kitchen order status update for %s: %s',
            order_id,
            ex.response.status_code
        )

        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/admin/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url=(
                f'/kitchen/orders/{order_id}?'
                'code=ORDER_SERVICE_HTTP_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        logger.exception(
            'Order-service unavailable while updating kitchen order %s.',
            order_id
        )
        return RedirectResponse(
            url=(
                f'/kitchen/orders/{order_id}?'
                'code=ORDER_SERVICE_HTTP_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=(
            f'/kitchen/orders/{order_id}?'
            'code=ORDER_STATUS_UPDATED'
        ),
        status_code=status.HTTP_303_SEE_OTHER
    )
