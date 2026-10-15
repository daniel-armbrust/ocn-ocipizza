#
# routes/admin_order_routes.py
#

import logging
from uuid import UUID

import httpx

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.forms.order_forms import OrderDeleteForm, OrderStatusForm
from app.messages.order_service_messages import ORDER_MESSAGES

from app.dependencies.authentication import get_admin_authenticated_session
from app.dependencies.templates import templates

from app.services.order_service import OrderService, get_order_service

router = APIRouter()
logger = logging.getLogger(__name__)

#
# GET: /admin/orders
#
@router.get(
    '/admin/orders',
    response_class=HTMLResponse
)
async def show_admin_orders(
    request: Request,
    code: str | None = None,
    selected_status: str | None = Query(default=None, alias='status'),
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: dict = Depends(get_admin_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Exibe a página de gerenciamento dos pedidos.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código opcional da mensagem apresentada no modal.
        selected_status: Estado utilizado para filtrar os pedidos.
        limit: Quantidade máxima de pedidos exibidos por página.
        offset: Quantidade de pedidos ignorados antes da página atual.
        session: Sessão administrativa validada pela dependência da rota.
        order_service: Serviço responsável pelas operações de pedidos.

    Returns:
        Página HTML contendo os pedidos disponíveis para administração.
    """

    message = ORDER_MESSAGES.get(code) if code else None

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

    pending_orders = sum(
        order.get('status') not in ('DELIVERED', 'CANCELLED')
        for order in orders
    )

    return templates.TemplateResponse(
        request=request,
        name='admin/orders.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'orders': orders,
            'total_orders': len(orders),
            'pending_orders': pending_orders,
            'received_count': received_count,
            'preparing_count': preparing_count,
            'ready_count': ready_count,
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
# GET: /admin/orders/{order_id}
#
@router.get(
    '/admin/orders/{order_id}',
    response_class=HTMLResponse
)
async def show_admin_order(
    request: Request,
    order_id: UUID,
    code: str | None = None,
    session: dict = Depends(get_admin_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Exibe os detalhes de um pedido para administração.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        order_id: Identificador UUID do pedido consultado.
        code: Código opcional da mensagem apresentada no modal.
        session: Sessão administrativa validada pela dependência da rota.
        order_service: Serviço responsável pelas operações de pedidos.

    Returns:
        Página HTML contendo os detalhes do pedido.
    """

    message = ORDER_MESSAGES.get(code) if code else None

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
        name='admin/order.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'order': order,
            'pending_orders': order_summary['pending_orders']
        }
    )

#
# POST: /admin/orders/{order_id}/status
#
@router.post('/admin/orders/{order_id}/status')
async def update_admin_order_status(
    request: Request,
    order_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Atualiza o status operacional de um pedido pela área administrativa.

    O BFF recebe a submissão do formulário HTML e delega a atualização ao
    order-service, que utiliza PATCH na comunicação interna.

    Args:
        request: Requisição HTTP contendo o novo status do pedido.
        order_id: Identificador UUID do pedido atualizado.
        session: Sessão administrativa validada pela dependência da rota.
        order_service: Serviço responsável pela comunicação com os pedidos.

    Returns:
        Redirecionamento para os detalhes do pedido com o resultado da operação.
    """

    form = OrderStatusForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=(
                f'/admin/orders/{order_id}?'
                'code=ORDER_SERVICE_VALIDATION_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    new_status = form.status.data

    allowed_statuses = {
        'RECEIVED',
        'PREPARING',
        'READY',
        'OUT_FOR_DELIVERY',
        'DELIVERED',
        'CANCELLED'
    }

    if new_status not in allowed_statuses:
        return RedirectResponse(
            url=(
                f'/admin/orders/{order_id}?'
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
            'Order-service rejected admin order status update for %s: %s',
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
                f'/admin/orders/{order_id}?'
                'code=ORDER_SERVICE_HTTP_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        logger.exception(
            'Order-service unavailable while updating admin order %s.',
            order_id
        )
        return RedirectResponse(
            url=(
                f'/admin/orders/{order_id}?'
                'code=ORDER_SERVICE_HTTP_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=(
            f'/admin/orders/{order_id}?'
            'code=ORDER_STATUS_UPDATED'
        ),
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# POST: /admin/orders/{order_id}/delete
#
@router.post('/admin/orders/{order_id}/delete')
async def delete_admin_order(
    request: Request,
    order_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Remove um pedido após a confirmação enviada pelo painel administrativo.

    Args:
        request: Requisição contendo o formulário de confirmação.
        order_id: Identificador UUID do pedido removido.
        session: Sessão administrativa validada pela dependência da rota.
        order_service: Serviço responsável pela comunicação com os pedidos.

    Returns:
        Redirecionamento para a lista de pedidos com o resultado da operação.
    """

    form = OrderDeleteForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=(
                f'/admin/orders/{order_id}?'
                'code=ORDER_SERVICE_VALIDATION_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await order_service.delete(
            access_token=session['access_token'],
            order_id=order_id
        )
    except httpx.HTTPStatusError as ex:
        logger.warning(
            'Order-service rejected admin order deletion for %s: %s',
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
                f'/admin/orders/{order_id}?'
                'code=ORDER_SERVICE_HTTP_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        logger.exception(
            'Order-service unavailable while deleting admin order %s.',
            order_id
        )
        return RedirectResponse(
            url=(
                f'/admin/orders/{order_id}?'
                'code=ORDER_SERVICE_HTTP_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/admin/orders?code=ORDER_DELETED',
        status_code=status.HTTP_303_SEE_OTHER
    )
