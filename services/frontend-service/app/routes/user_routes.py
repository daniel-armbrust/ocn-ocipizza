#
# routes/user_routes.py
#

import asyncio
import httpx

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.dependencies.authentication import get_authenticated_session
from app.forms.user_auth_forms import UserRegisterForm
from app.forms.user_forms import (
    UserAddressForm,
    UserWhatsappUpdateForm
)

from app.dependencies.templates import templates

from app.messages.user_service_messages import USER_MESSAGES
from app.messages.cart_messages import CART_MESSAGES
from app.services.order_service import OrderService, get_order_service
from app.services.user_service import UserService, get_user_service
from app.utils.http_utils import get_jsend_error_code

router = APIRouter()

#
# GET: /users/register
#
@router.get(
    '/users/register',
    response_class=HTMLResponse
)
async def show_register_page(
    request: Request,
    code: str | None = None
) -> HTMLResponse:
    """
    Renderiza a página utilizada para cadastro de usuários.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        code: Código funcional opcional associado à mensagem apresentada.

    Returns:
        Página HTML contendo o formulário de cadastro.
    """

    message = USER_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='users/register.html',
        context={
            'form': UserRegisterForm(),
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# GET: /users/confirm
#
@router.get(
    '/users/confirm'
)
async def confirm_user_email(
    token: str = Query(..., min_length=20, max_length=255),
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Confirma o e-mail do usuário a partir do token recebido na URL.

    Args:
        token: Token utilizado para confirmar o endereço de e-mail.
        user_service: Serviço responsável pelas operações relacionadas
            aos usuários.

    Returns:
        Redirecionamento para o login com o resultado da confirmação.
    """

    try:
        await user_service.confirm_email(token=token)
    except httpx.HTTPStatusError as ex:
        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_CONFIRMATION_ERROR'
        )

        return RedirectResponse(
            url=f'/users/login?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/login?code=USER_CONFIRMATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/users/login?code=USER_CONFIRMATION_SUCCESS',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# POST: /users/register
#
@router.post('/users/register')
@csrf_protect
async def register_user(
    request: Request,
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Processa o cadastro de um novo usuário.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        user_service: Serviço responsável pelo cadastro do usuário.

    Returns:
        Redirecionamento para o login em caso de sucesso ou para o cadastro
        com o código correspondente em caso de erro.
    """

    form_data = await request.form()

    form = UserRegisterForm(form_data)

    if not form.validate():
        return RedirectResponse(
            url='/users/register?code=USER_REGISTRATION_INVALID',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await user_service.create(
            full_name=form.full_name.data,
            email=form.email.data,
            whatsapp=form.whatsapp.data,
            password=form.password.data
        )
    except httpx.HTTPStatusError as ex:
        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_REGISTRATION_ERROR'
        )

        return RedirectResponse(
            url=f'/users/register?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/register?code=USER_REGISTRATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

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
    user_service: UserService = Depends(get_user_service)
) -> Response:
    """
    Renderiza as informações da conta do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para renderizar a página.
        code: Código funcional opcional utilizado para selecionar a mensagem
            apresentada no perfil.
        session: Sessão autenticada do usuário.
        user_service: Serviço responsável por compor os dados do perfil.

    Returns:
        Página do perfil ou redirecionamento para o login quando o access
        token não for mais válido.

    Raises:
        httpx.HTTPStatusError: Caso o user-service retorne uma falha diferente
            de uma resposta de autenticação.
        httpx.RequestError: Caso ocorra uma falha de comunicação com o
            user-service.
    """

    # Falhas HTTP e de comunicação são tratadas pelos handlers globais.
    user = await user_service.get_account(
        access_token=session.get('access_token')
    )

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
            'form': form,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'is_authenticated': True
        }
    )

#
# GET: /users/profile/addresses
#
@router.get(
    '/users/profile/addresses',
    response_class=HTMLResponse
)
async def show_addresses_page(
    request: Request,
    code: str | None = None,
    session=Depends(get_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> HTMLResponse:
    """
    Exibe os endereços do usuário dentro do painel da conta.

    Args:
        request: Requisição HTTP utilizada para renderizar a página.
        code: Código funcional opcional associado à mensagem apresentada.
        session: Sessão autenticada do usuário.
        user_service: Serviço responsável pelos dados da conta e endereços.

    Returns:
        Página HTML contendo os endereços cadastrados.

    Raises:
        httpx.HTTPStatusError: Caso o user-service rejeite a consulta.
        httpx.RequestError: Caso o user-service esteja indisponível.
    """

    # Falhas HTTP e de comunicação são tratadas pelos handlers globais.
    profile = await user_service.get_profile(
        access_token=session.get('access_token')
    )

    message = USER_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='users/addresses.html',
        context={
            'user': profile['user'],
            'addresses': profile['addresses'],
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'is_authenticated': True
        }
    )

#
# GET: /users/profile/orders
#
@router.get(
    '/users/profile/orders',
    response_class=HTMLResponse
)
async def show_orders_page(
    request: Request,
    code: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session=Depends(get_authenticated_session),
    user_service: UserService = Depends(get_user_service),
    order_service: OrderService = Depends(get_order_service)
) -> HTMLResponse:
    """
    Exibe o histórico de pedidos do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para renderizar a página.
        code: Código funcional opcional associado ao resultado do pedido.
        limit: Quantidade máxima de pedidos exibidos.
        offset: Quantidade de pedidos ignorados antes da consulta.
        session: Sessão autenticada do usuário.
        user_service: Serviço responsável pelos dados básicos da conta.
        order_service: Serviço responsável pela consulta dos pedidos.

    Returns:
        Página HTML contendo os pedidos retornados pelo order-service.

    Raises:
        httpx.HTTPStatusError: Caso um serviço rejeite a consulta.
        httpx.RequestError: Caso um serviço esteja indisponível.
    """

    access_token = session.get('access_token')

    # Falhas HTTP e de comunicação são tratadas pelos handlers globais.
    # Conta e pedidos são recursos independentes e podem ser consultados em
    # paralelo para reduzir o tempo de montagem do painel.
    user, orders = await asyncio.gather(
        user_service.get_account(access_token=access_token),
        order_service.get_all(
            access_token=access_token,
            limit=limit,
            offset=offset
        )
    )

    return templates.TemplateResponse(
        request=request,
        name='users/orders.html',
        context={
            'user': user,
            'orders': orders,
            # O sucesso do pedido é apresentado em modal; outros códigos
            # continuam disponíveis para a mensagem padrão do painel.
            'message': (
                None
                if code == 'CART_ORDER_SUCCESSFULLY_CREATED'
                else (CART_MESSAGES.get(code) or {}).get('message')
            ),
            'type': (
                None
                if code == 'CART_ORDER_SUCCESSFULLY_CREATED'
                else (CART_MESSAGES.get(code) or {}).get('type')
            ),
            'order_success_message': (
                CART_MESSAGES.get(code, {}).get('message')
                if code == 'CART_ORDER_SUCCESSFULLY_CREATED'
                else None
            ),
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
    code: str | None = None,
    session=Depends(get_authenticated_session)
) -> HTMLResponse:
    """
    Exibe a página para cadastro de um novo endereço do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para renderizar a página.
        code: Código funcional opcional associado à mensagem apresentada.
        session: Sessão autenticada do usuário.

    Returns:
        Página HTML contendo o formulário para cadastro de um novo endereço.
    """

    # Cria o formulário vazio com as regras de renderização e validação
    # definidas em `forms/user_forms.py`.
    form = UserAddressForm()
    message = USER_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='users/address_new.html',
        context={
            'form': form,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# POST: /users/profile/addresses/new
#
@router.post('/users/profile/addresses/new')
@csrf_protect
async def create_new_address(
    request: Request,
    session=Depends(get_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Processa o cadastro de um endereço do usuário autenticado.

    Args:
        request: Requisição HTTP contendo os dados do formulário.
        session: Sessão autenticada do usuário.
        user_service: Serviço responsável por cadastrar o endereço.

    Returns:
        Redirecionamento para a lista de endereços em caso de sucesso ou para
        o formulário com o código correspondente em caso de erro.
    """

    form = UserAddressForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url='/users/profile/addresses/new?code=USER_ADDRESS_INVALID',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await user_service.create_address(
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

        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_ADDRESS_CREATE_ERROR'
        )

        return RedirectResponse(
            url=f'/users/profile/addresses/new?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url=(
                '/users/profile/addresses/new'
                '?code=USER_ADDRESS_CREATE_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=(
            '/users/profile/addresses'
            '?code=USER_ADDRESS_SUCCESSFULLY_ADDED'
        ),
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# PUT: /users/profile/whatsapp
#
@router.put('/users/profile/whatsapp')
@csrf_protect
async def update_whatsapp(
    payload: dict,
    session=Depends(get_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Atualiza o número de WhatsApp do usuário autenticado.

    Args:
        payload: Novo número de WhatsApp informado pelo usuário.
        session: Obtém e valida a sessão autenticada do usuário.
        user_service: Serviço responsável por atualizar os dados do usuário.

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
        await user_service.update_whatsapp(
            access_token=session.get('access_token'),
            whatsapp=form.whatsapp.data
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_UPDATE_ERROR'
        )

        return RedirectResponse(
            url=f'/users/profile?code={code}',
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
    user_service: UserService = Depends(get_user_service)
) -> Response:
    """
    Remove um endereço do usuário autenticado.

    Args:
        request: Requisição HTTP utilizada para validar o token CSRF.
        address_id: Identificador único do endereço que será removido.
        session: Sessão autenticada do usuário.
        user_service: Serviço responsável por remover o endereço.

    Returns:
        Redirecionamento para a página de perfil com o resultado da operação.
    """

    try:
        await user_service.delete_address(
            access_token=session.get('access_token'),
            address_id=address_id
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        code = get_jsend_error_code(
            ex=ex,
            supported_codes=USER_MESSAGES,
            fallback='USER_ADDRESS_DELETE_ERROR'
        )

        return RedirectResponse(
            url=f'/users/profile/addresses?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/users/profile/addresses?code=USER_ADDRESS_DELETE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=(
            '/users/profile/addresses'
            '?code=USER_ADDRESS_SUCCESSFULLY_DELETED'
        ),
        status_code=status.HTTP_303_SEE_OTHER
    )
