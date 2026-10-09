#
# routes/user_auth_routes.py
#

import httpx

from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.config.settings import settings

from app.clients.user_auth_client import UserAuthClient, get_user_auth_client
from app.forms.user_auth_forms import UserLoginForm

from app.dependencies.templates import templates

from app.services.session_service import SessionService, get_session_service

from app.messages.user_messages import USER_MESSAGES

router = APIRouter()

#
# GET: /users/login
#
@router.get(
    '/users/login',
    response_class=HTMLResponse)
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
    user_client: UserAuthClient = Depends(
        get_user_auth_client
    ),
    session_service: SessionService = Depends(
        get_session_service
    )
) -> Response:
    """
    Processa a autenticação do usuário.

    Os dados recebidos pelo formulário são validados localmente
    através do WTForms antes que o user-service seja chamado.
    """

    form = UserLoginForm(
        await request.form()
    )

    # Interrompe o fluxo antes da chamada ao user-service caso
    # os dados informados não atendam às regras do formulário.
    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name='users/login.html',
            context={
                'form': form
            },
            status_code=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Encaminha ao user-service somente dados já validados
        # pelo frontend-service.
        payload = await user_client.login(
            email=form.email.data,
            password=form.password.data
        )

        # O contrato do user-service retorna os tokens dentro
        # do campo `data`.
        authentication = payload['data']

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
        payload = ex.response.json()

        # Utiliza USER_AUTHENTICATION_ERROR como fallback caso o código
        # retornado pelo user-service não esteja cadastrado em USER_MESSAGES.
        code = payload.get('data', {}).get(
            'code',
            'USER_AUTHENTICATION_ERROR'
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
    user_client: UserAuthClient = Depends(
        get_user_auth_client
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
        user_client: Cliente utilizado para comunicação com o
            user-service.
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
                await user_client.logout(
                    refresh_token=session['refresh_token']
                )

            except (
                httpx.HTTPStatusError,
                httpx.RequestError
            ):
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
