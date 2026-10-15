#
# routes/auth_routes.py
#

import logging

import httpx

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config.settings import settings

from starlette_wtf import csrf_protect

from app.forms.auth_forms import UserLoginForm

from app.services.admin_auth_service import (
    AdminAuthService,
    get_admin_auth_service
)

from app.services.session_service import (
    SessionService,
    get_session_service
)

from app.dependencies.templates import templates

from app.messages.user_service_messages import USER_MESSAGES

from app.exceptions.admin_auth_exceptions import (
    AdminAccessDeniedError,
    AdminAuthenticationError
)

router = APIRouter()
logger = logging.getLogger(__name__)

#
# GET: /admin/login
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
@router.post('/admin/login')
@csrf_protect
async def login_user(
    request: Request,
    admin_auth_service: AdminAuthService = Depends(
        get_admin_auth_service
    ),
    session_service: SessionService = Depends(
        get_session_service
    )
) -> RedirectResponse:
    """
    Autentica um usuário autorizado a acessar o admin-service.

    Usuários administrativos são direcionados ao painel administrativo,
    enquanto usuários da cozinha são direcionados ao painel da cozinha.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        admin_auth_service: Serviço responsável pela autenticação
            e autorização do usuário.
        session_service: Serviço responsável pelo gerenciamento
            das sessões no Redis.

    Returns:
        Redirecionamento para o painel correspondente ao perfil
        do usuário ou para a página de login em caso de falha.
    """

    form = UserLoginForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url='/admin/login?code=USER_AUTHENTICATION_INVALID',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # Autentica o usuário no user-service e verifica se ele possui
        # acesso administrativo ou acesso às funcionalidades da cozinha.
        authentication = await admin_auth_service.login(
            email=form.email.data,
            password=form.password.data
        )

        # Cria a sessão administrativa no Redis contendo somente
        # os dados necessários durante a navegação no admin-service.
        session_id = await session_service.create(
            user_id=authentication['user_id'],
            is_admin=authentication['is_admin'],
            is_kitchen=authentication['is_kitchen'],
            access_token=authentication['access_token'],
            refresh_token=authentication['refresh_token'],
            expires_in=authentication['expires_in']
        )
    except AdminAccessDeniedError as ex:
        logger.warning('Acesso ao admin-service negado: %s', ex)

        return RedirectResponse(
            url='/admin/login?code=USER_AUTHENTICATION_INVALID',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except AdminAuthenticationError:
        logger.exception('Falha ao autenticar usuário no admin-service.')

        return RedirectResponse(
            url='/admin/login?code=USER_AUTHENTICATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Administradores são direcionados para o painel administrativo e,
    # usuários da cozinha são direcionados para o painel operacional.
    if authentication['is_admin']:
        redirect_url = '/admin/dashboard?code=USER_AUTHENTICATION_SUCCESS'
    else:
        redirect_url = '/kitchen/orders?code=USER_AUTHENTICATION_SUCCESS'

    response = RedirectResponse(
        url=redirect_url,
        status_code=status.HTTP_303_SEE_OTHER
    )

    # Armazena no navegador somente o identificador da sessão.
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=settings.app_env != 'development',
        samesite=(
           'lax'
            if settings.app_env == 'development'
            else 'strict'
        ),
        max_age=settings.session_ttl,
        path='/'
    )

    return response

#
# POST: /admin/logout
# POST: /kitchen/logout
#
@router.post('/admin/logout')
@router.post('/kitchen/logout')
@csrf_protect
async def logout_user(
    request: Request,
    admin_auth_service: AdminAuthService = Depends(
        get_admin_auth_service
    ),
    session_service: SessionService = Depends(
        get_session_service
    )
) -> RedirectResponse:
    """
    Encerra uma sessão administrativa ou da cozinha.

    Quando a sessão existe, tenta revogar o refresh token no user-service e
    remove os dados locais independentemente do resultado da comunicação.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        admin_auth_service: Serviço responsável por solicitar a revogação da
            autenticação no user-service.
        session_service: Serviço responsável pelo gerenciamento das sessões
            locais do admin-service.

    Returns:
        Redirecionamento para a página de login.
    """

    session_id = request.cookies.get(
        settings.session_cookie_name
    )

    if session_id:
        session = await session_service.get(
            session_id=session_id
        )

        if session:
            refresh_token = session.get('refresh_token')

            if refresh_token:
                try:
                    await admin_auth_service.logout(
                        refresh_token=refresh_token
                    )
                except httpx.HTTPStatusError as ex:
                    logger.warning(
                        'User-service rejected session revocation with '
                        'status %s.',
                        ex.response.status_code
                    )
                except httpx.RequestError:
                    logger.exception(
                        'User-service unavailable while revoking session.'
                    )

            # O logout local não depende da disponibilidade do user-service.
            await session_service.delete(
                session_id=session_id
            )

    response = RedirectResponse(
        url='/admin/login?code=USER_LOGOUT_SUCCESS',
        status_code=status.HTTP_303_SEE_OTHER
    )

    response.delete_cookie(
        key=settings.session_cookie_name,
        path='/'
    )

    return response
