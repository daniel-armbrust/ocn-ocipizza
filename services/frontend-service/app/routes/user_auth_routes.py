#
# routes/user_auth_routes.py
#

import httpx

from fastapi import APIRouter, Depends, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.config.settings import settings

from app.forms.user_auth_forms import (
    UserLoginForm,
    UserPasswordResetConfirmForm,
    UserPasswordResetRequestForm
)

from app.dependencies.templates import templates

from app.services.session_service import SessionService, get_session_service
from app.services.user_auth_service import (
    UserAuthService,
    get_user_auth_service
)

from app.messages.user_service_messages import USER_MESSAGES
from app.utils.http_utils import get_jsend_error_code

router = APIRouter()

#
# GET: /users/login
#
@router.get(
    '/users/login',
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
        request: Requisição HTTP recebida pelo frontend-service.
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
# POST: /users/login
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
    """
    Processa a autenticação do usuário.

    Os dados recebidos pelo formulário são validados localmente
    através do WTForms antes que o user-service seja chamado.

    Args:
        request: Requisição contendo os dados submetidos pelo formulário.
        user_auth_service: Serviço responsável por coordenar a autenticação
            junto ao user-service.
        session_service: Serviço responsável por criar a sessão local do BFF.

    Returns:
        Redirecionamento após a autenticação ou para o login com o código
        correspondente em caso de erro.
    """

    form = UserLoginForm(await request.form())

    # Interrompe o fluxo antes da chamada ao user-service caso
    # os dados informados não atendam às regras do formulário.
    if not form.validate():
        return RedirectResponse(
            url='/users/login?code=USER_AUTHENTICATION_INVALID',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        # O serviço recebe somente dados já validados pelo frontend-service e
        # devolve as credenciais necessárias à criação da sessão local.
        authentication = await user_auth_service.authenticate(
            email=form.email.data,
            password=form.password.data
        )

        # Cria uma sessão no BFF (Backend For Frontend). Os tokens
        # permanecem armazenados no backend através do repositório de
        # sessões configurado, que pode utilizar Redis, Oracle NoSQL
        # ou SQLAlchemy, sem expor esses dados diretamente ao navegador.
        session_id = await session_service.create(
            access_token=authentication['access_token'],
            refresh_token=authentication['refresh_token'],
            expires_in=authentication['expires_in']
        )
    except httpx.HTTPStatusError as ex:
        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_AUTHENTICATION_ERROR'
        )

        # Insere o código na URL e redireciona para a página de login,
        # onde a mensagem correspondente será exibida ao usuário.
        return RedirectResponse(
            url=f'/users/login?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/login?code=USER_AUTHENTICATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    response = RedirectResponse(
        url='/pizzas?code=USER_AUTHENTICATION_SUCCESS',
        status_code=status.HTTP_303_SEE_OTHER
    )

    # Cria o cookie contendo apenas o identificador opaco da sessão,
    # mantendo os tokens armazenados exclusivamente no backend.
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
        path='/'
    )

    return response

#
# POST: /users/logout
#
@router.post('/users/logout')
@csrf_protect
async def logout_user(
    request: Request,
    user_auth_service: UserAuthService = Depends(
        get_user_auth_service
    ),
    session_service: SessionService = Depends(
        get_session_service
    )
) -> RedirectResponse:
    """
    Encerra a sessão do usuário no frontend-service.

    Caso exista uma sessão válida no BFF, recupera o refresh token
    armazenado no backend e solicita ao user-service a revogação da
    sessão correspondente. Em seguida, remove a sessão local e o
    cookie utilizado pelo navegador.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        user_auth_service: Serviço responsável por coordenar a revogação
            da autenticação junto ao user-service.
        session_service: Serviço responsável pelo gerenciamento
            das sessões do frontend-service.

    Returns:
        Redirecionamento para a página de login.
    """

    # Recupera o identificador opaco da sessão enviado pelo navegador.
    session_id = request.cookies.get(
        settings.session_cookie_name
    )

    if session_id:
        # Recupera os dados da sessão armazenados no repositório
        # configurado, que pode utilizar Redis, Oracle NoSQL ou
        # SQLAlchemy.
        session = await session_service.get(
            session_id=session_id
        )

        if session:
            try:
                # Solicita ao user-service a revogação do refresh token
                # associado à sessão antes de remover os dados locais.
                await user_auth_service.logout(
                    refresh_token=session['refresh_token']
                )

            except (httpx.HTTPStatusError, httpx.RequestError):
                # O logout local continua mesmo que o user-service
                # esteja indisponível ou não consiga revogar o token.
                # Dessa forma, o navegador perde imediatamente o acesso
                # à sessão mantida pelo frontend-service.
                pass

            # Remove a sessão do repositório local independentemente
            # do resultado da revogação no user-service.
            await session_service.delete(
                session_id=session_id
            )

    response = RedirectResponse(
        url='/pizzas',
        status_code=status.HTTP_303_SEE_OTHER
    )

    # Remove o cookie mesmo quando ele não corresponde mais a uma
    # sessão existente no backend.
    response.delete_cookie(
        key=settings.session_cookie_name,
        path='/'
    )

    return response

#
# GET: /users/password-reset
#
@router.get(
    '/users/password-reset',
    response_class=HTMLResponse
)
async def show_password_reset_page(
    request: Request,
    code: str | None = None
) -> HTMLResponse:
    """
    Exibe a página utilizada para solicitar a redefinição de senha.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        code: Código funcional opcional associado à mensagem apresentada.

    Returns:
        Página HTML contendo o formulário de solicitação.
    """

    message = USER_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='users/password_reset.html',
        context={
            'form': UserPasswordResetRequestForm(),
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# POST: /users/password-reset
#
@router.post('/users/password-reset')
@csrf_protect
async def request_password_reset(
    request: Request,
    user_auth_service: UserAuthService = Depends(
        get_user_auth_service
    )
) -> RedirectResponse:
    """
    Solicita a redefinição da senha do usuário.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        user_auth_service: Serviço responsável pelas operações relacionadas
            à autenticação dos usuários.

    Returns:
        Redirecionamento para a página de solicitação de redefinição
        de senha com o resultado da operação.
    """

    form = UserPasswordResetRequestForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url='/users/login?code=USER_PASSWORD_RESET_INVALID',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await user_auth_service.request_password_reset(
            email=form.email.data
        )
    except httpx.HTTPStatusError as ex:
        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_PASSWORD_RESET_ERROR'
        )

        return RedirectResponse(
            url=f'/users/login?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/login?code=USER_PASSWORD_RESET_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Retorna uma mensagem genérica independentemente da existência
    # da conta associada ao endereço de e-mail informado.
    return RedirectResponse(
        url='/users/login?code=USER_PASSWORD_RESET_REQUESTED',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# GET: /users/password-reset/confirm
#
@router.get(
    '/users/password-reset/confirm',
    response_class=HTMLResponse
)
async def show_password_reset_confirm_page(
    request: Request,
    token: str = Query(..., min_length=20, max_length=4096)
) -> HTMLResponse:
    """
    Exibe a página utilizada para definir uma nova senha.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        token: Token recebido no link enviado por e-mail.

    Returns:
        Página HTML contendo o formulário de redefinição de senha.
    """

    return templates.TemplateResponse(
        request=request,
        name='users/password_reset_confirm.html',
        context={
            'form': UserPasswordResetConfirmForm(
                data={'token': token}
            )
        }
    )

#
# POST: /users/password-reset/confirm
#
@router.post('/users/password-reset/confirm')
@csrf_protect
async def confirm_password_reset(
    request: Request,
    user_auth_service: UserAuthService = Depends(
        get_user_auth_service
    )
) -> RedirectResponse:
    """
    Confirma a redefinição de senha utilizando o token recebido por e-mail.

    Args:
        request: Requisição HTTP contendo o token e as novas senhas.
        user_auth_service: Serviço responsável pelas operações relacionadas
            à autenticação dos usuários.

    Returns:
        Redirecionamento para o login com o código correspondente ao resultado
        da operação.
    """

    form = UserPasswordResetConfirmForm(await request.form())

    if not form.validate():
        code = (
            'USER_INVALID_PASSWORD_RESET_TOKEN'
            if form.token.errors
            else 'USER_PASSWORD_RESET_CONFIRM_INVALID'
        )

        return RedirectResponse(
            url=f'/users/login?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await user_auth_service.confirm_password_reset(
            token=form.token.data,
            new_password=form.new_password.data,
            confirm_new_password=form.confirm_new_password.data
        )
    except httpx.HTTPStatusError as ex:
        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_PASSWORD_RESET_ERROR'
        )

        return RedirectResponse(
            url=f'/users/login?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/login?code=USER_PASSWORD_RESET_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/users/login?code=USER_PASSWORD_RESET_SUCCESS',
        status_code=status.HTTP_303_SEE_OTHER
    )
