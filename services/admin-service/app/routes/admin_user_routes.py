#
# routes/admin_user_routes.py
#

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from app.messages.user_service_messages import USER_MESSAGES

from app.dependencies.authentication import get_admin_authenticated_session
from app.dependencies.templates import templates

from app.services.order_service import OrderService, get_order_service

router = APIRouter()

#
# GET: /admin/dashboard
#
@router.get(
    '/admin/dashboard',
    response_class=HTMLResponse
)
async def show_admin_dashboard(
    request: Request,
    code: str | None = None,
    session: dict = Depends(get_admin_authenticated_session),
    order_service: OrderService = Depends(get_order_service)
) -> Response:
    """
    Exibe a página principal do painel administrativo.

    A dependência de autenticação garante que exista uma sessão válida e
    que o usuário possua permissão administrativa antes da renderização.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código opcional da mensagem que será exibida na página.
        session: Sessão administrativa validada pela dependência da rota.
        order_service: Serviço responsável pelas operações de pedidos.

    Returns:
        Página HTML com a visão geral do painel administrativo.
    """

    message = USER_MESSAGES.get(code) if code else None

    order_summary = await order_service.get_summary(
        access_token=session['access_token']
    )

    return templates.TemplateResponse(
        request=request,
        name='admin/dashboard.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'orders_today': order_summary['orders_today'],
            'orders_preparing': order_summary['orders_preparing'],
            'orders_ready': order_summary['orders_ready'],
            'pending_orders': order_summary['pending_orders']
        }
    )
