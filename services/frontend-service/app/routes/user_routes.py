#
# routes/user_routes.py
#

import httpx

from uuid import UUID

from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.clients.user_client import UserClient, get_user_client
from app.dependencies.authentication import get_authenticated_session
from app.forms.user_auth_forms import UserRegisterForm
from app.forms.user_forms import UserAddressForm, UserWhatsappUpdateForm

from app.dependencies.templates import templates

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
@csrf_protect
async def register_user(
    request: Request,
    user_client: UserClient = Depends(get_user_client)
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
        url='/users/login?code=USER_CONFIRMATION_SENT',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# GET: /users/profile
#
@router.get(
    '/users/profile',
    response_class=HTMLResponse
)
async def show_profile_page(
    request: Request,
    code: str | None = None,
    session=Depends(get_authenticated_session),
    user_client: UserClient = Depends(get_user_client)
) -> Response:
    """
    Renderiza os dados pessoais e os endereços do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para renderizar a página.
        code: Código funcional opcional utilizado para selecionar a mensagem
            apresentada no perfil.
        session: Sessão autenticada do usuário.
        user_client: Cliente responsável pela comunicação com o user-service.

    Returns:
        Página do perfil ou redirecionamento para o login quando o access
        token não for mais válido.

    Raises:
        httpx.HTTPStatusError: Caso o user-service retorne uma falha diferente
            de uma resposta de autenticação.
        httpx.RequestError: Caso ocorra uma falha de comunicação com o
            user-service.
    """

    try:
        user = await user_client.get_profile(
            access_token=session.get('access_token')
        )
        addresses = await user_client.get_addresses(
            access_token=session.get('access_token')
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        raise

    form = UserWhatsappUpdateForm(
        data={'whatsapp': user.get('whatsapp')}
    )

    message = None

    if code:
        message = USER_MESSAGES.get(
            code,
            {
                'message': 'Não foi possível processar a operação solicitada.',
                'type': 'error'
            }
        )

    return templates.TemplateResponse(
        request=request,
        name='users/profile.html',
        context={
            'user': user,
            'addresses': addresses,
            'form': form,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'is_authenticated': True
        }
    )

#
# GET: /users/profile/addresses/new
#
@router.get(
    '/users/profile/addresses/new',
    response_class=HTMLResponse
)
async def show_new_address_page(
    request: Request,
    session=Depends(get_authenticated_session)
) -> HTMLResponse:
    """
    Exibe a página para cadastro de um novo endereço do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para renderizar a página.
        session: Sessão autenticada do usuário.

    Returns:
        Página HTML contendo o formulário para cadastro de um novo endereço.
    """

    # Cria o formulário vazio com as regras de renderização e validação
    # definidas em `forms/user_forms.py`.
    form = UserAddressForm()

    return templates.TemplateResponse(
        request=request,
        name='users/address_new.html',
        context={'form': form}
    )

#
# POST: /users/profile/addresses/new
#
@router.post(
    '/users/profile/addresses/new',
    response_class=HTMLResponse
)
@csrf_protect
async def create_new_address(
    request: Request,
    session=Depends(get_authenticated_session),
    user_client: UserClient = Depends(get_user_client)
) -> Response:
    """
    Processa o cadastro de um endereço do usuário autenticado.

    Args:
        request: Requisição HTTP contendo os dados do formulário.
        session: Sessão autenticada do usuário.
        user_client: Cliente responsável pela comunicação com o user-service.

    Returns:
        Redirecionamento para o perfil em caso de sucesso ou página do
        formulário contendo os erros encontrados.
    """

    form = UserAddressForm(await request.form())

    if not form.validate():
        return templates.TemplateResponse(
            request=request,
            name='users/address_new.html',
            context={'form': form},
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT
        )

    try:
        await user_client.create_address(
            access_token=session.get('access_token'),
            label=form.label.data,
            zip_code=form.zip_code.data,
            street=form.street.data,
            number=form.number.data,
            complement=form.complement.data,
            neighborhood=form.neighborhood.data,
            city=form.city.data,
            state=form.state.data,
            is_default=form.is_default.data
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        payload = ex.response.json()

        message = USER_MESSAGES.get(
            payload.get('data', {}).get('code'),
            {
                'message': 'Não foi possível cadastrar o endereço.',
                'type': 'error'
            }
        )

        return templates.TemplateResponse(
            request=request,
            name='users/address_new.html',
            context={
                'form': form,
                'message': message['message'],
                'type': message['type']
            },
            status_code=ex.response.status_code
        )
    except httpx.RequestError:
        return templates.TemplateResponse(
            request=request,
            name='users/address_new.html',
            context={
                'form': form,
                'message': (
                    'O serviço de usuários está temporariamente indisponível.'
                ),
                'type': 'error'
            },
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE
        )

    return RedirectResponse(
        url='/users/profile?code=USER_ADDRESS_SUCCESSFULLY_ADDED',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# PUT: /users/profile/whatsapp
#
@router.put('/users/profile/whatsapp')
@csrf_protect
async def update_whatsapp(
    payload: dict,
    session = Depends(get_authenticated_session),
    user_client: UserClient = Depends(get_user_client)
) -> Response:
    """
    Atualiza o número de WhatsApp do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para validar o token CSRF.
        payload: Novo número de WhatsApp informado pelo usuário.
        session: Obtém e valida a sessão autenticada do usuário.
        user_client: Cliente responsável pela comunicação com o user-service.

    Returns:
        Redirecionamento para o perfil contendo o código correspondente ao
        resultado da atualização.
    """

    form = UserWhatsappUpdateForm(data=payload)

    if not form.validate():
        return RedirectResponse(
            url='/users/profile?code=USER_UPDATE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await user_client.update_whatsapp(
            access_token=session.get('access_token'),
            whatsapp=form.whatsapp.data
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url=f'/users/profile?code=USER_UPDATE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/profile?code=USER_UPDATE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/users/profile?code=USER_WHATSAPP_UPDATED',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# DELETE: /users/profile/addresses/{address_id}
#
@router.delete(
    '/users/profile/addresses/{address_id}'
)
@csrf_protect
async def delete_user_address(
    request: Request,
    address_id: UUID,
    session=Depends(get_authenticated_session),
    user_client: UserClient = Depends(get_user_client)
) -> Response:
    """
    Remove um endereço do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para validar o token CSRF.
        address_id: Identificador único do endereço que será removido.
        session: Sessão autenticada do usuário.
        user_client: Cliente responsável pela comunicação com o user-service.

    Returns:
        Redirecionamento para a página de perfil com o resultado da operação.
    """

    try:
        await user_client.delete_address(
            access_token=session.get('access_token'),
            address_id=address_id
        )
    except httpx.HTTPStatusError as ex:
        # Redireciona para o login quando o access token não for mais válido.
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Redireciona para o perfil informando que não foi possível
        # remover o endereço.
        return RedirectResponse(
            url='/users/profile?code=USER_ADDRESS_DELETE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/profile?code=USER_ADDRESS_DELETE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/users/profile?code=USER_ADDRESS_SUCCESSFULLY_DELETED',
        status_code=status.HTTP_303_SEE_OTHER
    )
