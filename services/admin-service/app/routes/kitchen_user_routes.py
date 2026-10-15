#
# routes/kitchen_user_routes.py
#

from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse

from app.messages.user_service_messages import USER_MESSAGES

from app.dependencies.authentication import get_kitchen_authenticated_session
from app.dependencies.templates import templates

router = APIRouter()

#
# GET: /kitchen/dashboard
#
@router.get(
    '/kitchen/dashboard',
    response_class=HTMLResponse
)
async def show_kitchen_dashboard(
    request: Request,
    code: str | None = None,
    session: dict = Depends(get_kitchen_authenticated_session)
) -> Response:
    """
    Exibe a página principal do painel operacional da cozinha.

    A dependência de autenticação garante que exista uma sessão válida e
    que o usuário possua acesso às funcionalidades da cozinha antes da
    renderização.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código opcional da mensagem que será exibida na página.
        session: Sessão da cozinha validada pela dependência da rota.

    Returns:
        Página HTML com a visão operacional dos pedidos da cozinha.
    """

    message = USER_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='kitchen/dashboard.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )
