#
# routes/user_routes.py
#

import httpx

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config.settings import settings

from app.clients.user_client import UserClient, get_user_client
from app.forms.user import UserLoginForm, UserRegisterForm

from app.dependencies.templates import templates

from app.services.session_service import SessionService, get_session_service

from app.messages.user_messages import USER_MESSAGES

router = APIRouter()

#
# GET: /users/register
#
@router.get(
    '/users/register',
    response_class=HTMLResponse
)
def show_register_page(request: Request) -> HTMLResponse:
    """
    Renderiza a página utilizada para cadastro de usuários.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.

    Returns:
        Página HTML contendo o formulário de cadastro.
    """

    return templates.TemplateResponse(
        request=request,
        name='users/register.html',
        context={'form': UserRegisterForm()}
    )

#
# POST: /users/register
#
@router.post(
    '/users/register',
    response_class=HTMLResponse
)
async def register_user(
    request: Request,
    user_client: UserClient = Depends(
        get_user_client
    )
) -> HTMLResponse:
    """
    Processa o cadastro de um novo usuário.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        user_client: Cliente utilizado para comunicação com o
            user-service.

    Returns:
        Redirecionamento para a página de login em caso de sucesso
        ou página de cadastro contendo a mensagem de erro.
    """

    form_data = await request.form()
    
    form = UserRegisterForm(form_data)

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name='users/register.html',
            context={'form': form},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    try:
        await user_client.create(
            full_name=form.full_name.data,
            email=form.email.data,
            whatsapp=form.whatsapp.data,
            password=form.password.data
        )
    except httpx.HTTPStatusError as ex:
        payload = ex.response.json()

        message = USER_MESSAGES.get(
            payload.get('data', {}).get('code'),
            {
                'message': 'Não foi possível realizar o cadastro.',
                'type': 'error'
            }
        )

        return templates.TemplateResponse(
            request=request,
            name='users/register.html',
            context={
                'message': message['message'],
                'type': message['type'],
                'form': form
            },
            status_code=ex.response.status_code
        )
    except httpx.RequestError:
        return templates.TemplateResponse(
            request=request,
            name='users/register.html',
            context={
                'message': (
                    'O serviço de usuários está temporariamente indisponível.'
                ),
                'type': 'error',
                'form': form
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Após o cadastro bem-sucedido, redireciona o usuário
    # para a página de autenticação com o indicador que apresenta
    # as orientações de confirmação do cadastro.
    return RedirectResponse(
        url='/users/login?registration=success',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# GET: /users/login
#
@router.get(
    '/users/login',
    response_class=HTMLResponse
)
def show_login_page(
    request: Request,
    registration: str | None = None
) -> HTMLResponse:
    """
    Renderiza a página utilizada para autenticação de usuários.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        registration: Resultado do cadastro usado para apresentar a
            orientação de confirmação da conta.

    Returns:
        Página HTML contendo o formulário de autenticação.
    """

    return templates.TemplateResponse(
        request=request,
        name='users/login.html',
        context={
            'message': (
                'Enviamos um e-mail para você. Acesse o link recebido '
                'para confirmar seu cadastro antes de entrar.'
                if registration == 'success' else None
                
            ),
            'type': 'info',
            'form': UserLoginForm()
        }
    )

#
# POST: /users/login
#
@router.post(
    '/users/login',
    response_class=HTMLResponse
)
async def login_user(
    request: Request,
    user_client: UserClient = Depends(
        get_user_client
    ),
    session_service: SessionService = Depends(
        get_session_service
    )
) -> HTMLResponse:
    """
    Processa a autenticação de um usuário.

    Após a autenticação no user-service, cria uma sessão no BFF
    contendo os tokens retornados e envia ao navegador somente
    o identificador da sessão através de um cookie HttpOnly.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        user_client: Cliente utilizado para comunicação com o
            user-service.
        session_service: Serviço responsável pelo gerenciamento
            das sessões do frontend-service.

    Returns:
        Redirecionamento após autenticação bem-sucedida ou página
        de login contendo a mensagem de erro.
    """

    form_data = await request.form()
    form = UserLoginForm(form_data)

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name='users/login.html',
            context={'form': form},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    try:
        payload = await user_client.login(
            email=form.email.data,
            password=form.password.data
        )

        # Obtém os tokens retornados pelo user-service.
        authentication = payload['data']

        # Cria uma sessão no BFF associando um identificador opaco
        # aos tokens utilizados para comunicação com os microserviços.
        session_id = await session_service.create(
            access_token=authentication['access_token'],
            refresh_token=authentication['refresh_token'],
            expires_in=authentication['expires_in']
        )
    except httpx.HTTPStatusError as ex:
        # Trata credenciais inválidas ou outras respostas de erro
        # retornadas pelo user-service.
        payload = ex.response.json()

        message = USER_MESSAGES.get(
            payload.get('data', {}).get('code'),
            {
                'message': 'Não foi possível realizar a autenticação.',
                'type': 'error'
            }
        )

        return templates.TemplateResponse(
            request=request,
            name='users/login.html',
            context={
                'message': message['message'],
                'type': message['type'],
                'form': form
            },
            status_code=ex.response.status_code
        )   
    except httpx.RequestError:
        # Trata falhas de comunicação, timeout ou indisponibilidade
        # temporária do user-service.
        return templates.TemplateResponse(
            request=request,
            name='users/login.html',
            context={
                'message': (
                    'O serviço de usuários está temporariamente indisponível.'
                ),
                'type': 'error',
                'form': form
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    # Redireciona o usuário após a autenticação bem-sucedida.
    # TODO: exibir mensagem de autenticação bem sucedida.
    response = RedirectResponse(
        url='/pizzas',
        status_code=status.HTTP_303_SEE_OTHER
    )

    # O navegador recebe somente o identificador opaco da sessão.
    # Access token e refresh token permanecem armazenados no BFF.
    response.set_cookie(
        key=settings.session_cookie_name,
        value=session_id,
        httponly=True,
        secure=settings.app_env != 'development',
        samesite='lax' if settings.app_env == 'development' else 'strict',
        path='/'
    )

    return response
