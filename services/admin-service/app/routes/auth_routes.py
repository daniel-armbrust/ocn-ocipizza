#
# routes/auth_routes.py
#

import httpx

from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.forms.auth_forms import UserLoginForm

from app.dependencies.authentication import get_authenticated_session

from app.dependencies.templates import templates

from app.messages.user_service_messages import USER_MESSAGES

router = APIRouter()

#
# GET  /admin/login
#
@router.get(
    '/admin/login',
    response_class=HTMLResponse
)
async def show_login_page(
    request: Request,
    code: str | None = None
) -> HTMLResponse:
    """
    Exibe a página de autenticação.

    Quando um código é informado na URL, traduz o código funcional
    para a mensagem correspondente antes de renderizar o template.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código funcional opcional utilizado para identificar
            uma mensagem a ser exibida ao usuário.

    Returns:
        Página HTML contendo o formulário de autenticação.
    """

    # Cria o formulário vazio que será utilizado pelo template.
    form = UserLoginForm()

    # Recupera a mensagem correspondente ao código informado na URL.
    # Caso o código não exista no mapeamento, utiliza uma mensagem
    # genérica de autenticação.
    message = None

    if code:
        message = USER_MESSAGES.get(
            code,
            {
                'message': 'Não foi possível realizar a autenticação.',
                'type': 'error'
            }
        )

    return templates.TemplateResponse(
        request=request,
        name='users/login.html',
        context={
            'form': form,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# POST: /admin/login
#
@router.post('/users/login')
@csrf_protect
async def login_user(
    request: Request,
    user_auth_service: UserAuthService = Depends(
        get_user_auth_service
    ),
    session_service: SessionService = Depends(
        get_session_service
    )
) -> RedirectResponse:

#
# POST /admin/logout
#