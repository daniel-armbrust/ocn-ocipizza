#
# routes/admin_user_routes.py
#

import re
from uuid import UUID

import httpx

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.messages.user_service_messages import USER_MESSAGES

from app.dependencies.authentication import get_admin_authenticated_session
from app.dependencies.templates import templates

from app.forms.user_forms import (
    UserCreateForm,
    UserDeleteForm,
    UserUpdateForm
)

from app.services.order_service import OrderService, get_order_service
from app.services.user_service import UserService, get_user_service

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

#
# GET: /admin/users
#
@router.get(
    '/admin/users',
    response_class=HTMLResponse
)
async def show_admin_users(
    request: Request,
    code: str | None = None,
    search: str | None = None,
    role: str | None = None,
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: dict = Depends(get_admin_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> Response:
    """
    Exibe a página de administração de usuários.

    A rota é responsável por validar o acesso administrativo, solicitar os
    dados ao serviço de usuários e renderizar o template. A comunicação HTTP
    permanece encapsulada no `UserService` e em seu cliente.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código opcional da mensagem exibida após uma operação.
        search: Texto utilizado para filtrar usuários por e-mail.
        role: Perfil utilizado para filtrar usuários.
        limit: Quantidade máxima de usuários exibidos por página.
        offset: Quantidade de usuários ignorados antes da página atual.
        session: Sessão administrativa validada pela dependência da rota.
        user_service: Serviço responsável pelas operações de usuários.

    Returns:
        Página HTML do painel de administração de usuários.
    """

    message = USER_MESSAGES.get(code) if code else None

    users = await user_service.get_all(
        access_token=session['access_token'],
        email=search,
        is_admin=True if role == 'admin' else None,
        is_kitchen=True if role == 'kitchen' else None,
        limit=limit + 1,
        offset=offset
    )

    # Usuários regulares são identificados pela ausência dos dois perfis
    # administrativos, pois esse filtro não existe no contrato upstream.
    if role == 'regular':
        users = [
            user for user in users
            if not user.get('is_admin') and not user.get('is_kitchen')
        ]

    has_next_page = len(users) > limit
    users = users[:limit]

    return templates.TemplateResponse(
        request=request,
        name='users/users.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'users': users,
            'search': search,
            'role': role,
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
# GET: /admin/users/new
#
@router.get(
    '/admin/users/new',
    response_class=HTMLResponse
)
async def show_new_admin_user(
    request: Request,
    _: dict = Depends(get_admin_authenticated_session)
) -> Response:
    """
    Exibe o formulário de cadastro de um novo usuário.

    A rota apenas valida a sessão administrativa e renderiza o template. O
    processamento do formulário será implementado em uma rota de submissão
    própria, que deverá delegar a operação a um serviço.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        _: Sessão administrativa validada pela dependência da rota.

    Returns:
        Página HTML contendo o formulário de novo usuário.
    """

    return templates.TemplateResponse(
        request=request,
        name='users/user.html',
        context={
            'user': None
        }
    )

#
# GET: /admin/users/{user_id}
#
@router.get(
    '/admin/users/{user_id:uuid}',
    response_class=HTMLResponse
)
async def show_admin_user(
    request: Request,
    user_id: UUID,
    code: str | None = None,
    session: dict = Depends(get_admin_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> Response:
    """
    Exibe os dados de um usuário para consulta e edição.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        user_id: Identificador UUID do usuário consultado.
        code: Código opcional da mensagem exibida após uma operação.
        session: Sessão administrativa validada pela dependência da rota.
        user_service: Serviço responsável pela consulta do usuário.

    Returns:
        Página HTML com os dados do usuário selecionado.
    """

    user = await user_service.get_by_id(
        access_token=session['access_token'],
        user_id=user_id
    )

    message = USER_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='users/user.html',
        context={
            'user': user,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# POST: /admin/users
#
@router.post('/admin/users')
@csrf_protect
async def create_admin_user(
    request: Request,
    session: dict = Depends(get_admin_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Cria um usuário através do formulário administrativo.

    Args:
        request: Requisição contendo os dados do formulário.
        session: Sessão administrativa validada pela dependência da rota.
        user_service: Serviço responsável pela criação do usuário.

    Returns:
        Redirecionamento para a listagem com o resultado da operação.
    """

    form = UserCreateForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url='/admin/users/new?code=USER_VALIDATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    whatsapp = re.sub(r'\D', '', form.whatsapp.data or '')

    if len(whatsapp) != 11:
        return RedirectResponse(
            url='/admin/users/new?code=USER_VALIDATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    role = form.role.data

    payload = {
        'full_name': form.full_name.data,
        'email': form.email.data,
        'whatsapp': whatsapp,
        'password': form.password.data,
        'confirmed': form.confirmed.data,
        'is_admin': role == 'admin',
        'is_kitchen': role == 'kitchen'
    }

    try:
        await user_service.create(
            access_token=session['access_token'],
            payload=payload
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/admin/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        if ex.response.status_code == status.HTTP_409_CONFLICT:
            return RedirectResponse(
                url='/admin/users/new?code=USER_ALREADY_REGISTERED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        if ex.response.status_code in {
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        }:
            return RedirectResponse(
                url='/admin/users/new?code=USER_VALIDATION_ERROR',
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url='/admin/users/new?code=USER_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/admin/users/new?code=USER_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/admin/users?code=USER_CREATED',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# POST: /admin/users/{user_id}
#
@router.post('/admin/users/{user_id:uuid}')
@csrf_protect
async def update_admin_user(
    request: Request,
    user_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Atualiza os dados administrativos de um usuário.

    Args:
        request: Requisição contendo os dados do formulário.
        user_id: Identificador UUID do usuário atualizado.
        session: Sessão administrativa validada pela dependência da rota.
        user_service: Serviço responsável pela atualização do usuário.

    Returns:
        Redirecionamento para os dados do usuário com o resultado da operação.
    """

    form = UserUpdateForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_VALIDATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    whatsapp = re.sub(r'\D', '', form.whatsapp.data or '')

    if len(whatsapp) != 11:
        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_VALIDATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    role = form.role.data

    payload = {
        'full_name': form.full_name.data,
        'email': form.email.data,
        'whatsapp': whatsapp,
        'confirmed': form.confirmed.data,
        'is_admin': role == 'admin',
        'is_kitchen': role == 'kitchen'
    }

    try:
        await user_service.update(
            access_token=session['access_token'],
            user_id=user_id,
            payload=payload
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/admin/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        if ex.response.status_code == status.HTTP_404_NOT_FOUND:
            return RedirectResponse(
                url='/admin/users?code=USER_NOT_FOUND',
                status_code=status.HTTP_303_SEE_OTHER
            )

        if ex.response.status_code == status.HTTP_409_CONFLICT:
            return RedirectResponse(
                url=f'/admin/users/{user_id}?code=USER_ALREADY_REGISTERED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        if ex.response.status_code in {
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_422_UNPROCESSABLE_ENTITY
        }:
            return RedirectResponse(
                url=f'/admin/users/{user_id}?code=USER_VALIDATION_ERROR',
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=f'/admin/users?code=USER_UPDATED',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# POST: /admin/users/{user_id}/delete
#
@router.post('/admin/users/{user_id:uuid}/delete')
@csrf_protect
async def delete_admin_user(
    request: Request,
    user_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    user_service: UserService = Depends(get_user_service)
) -> RedirectResponse:
    """
    Exclui um usuário após a confirmação do formulário.

    Args:
        request: Requisição contendo o formulário de confirmação.
        user_id: Identificador UUID do usuário removido.
        session: Sessão administrativa validada pela dependência da rota.
        user_service: Serviço responsável pela exclusão do usuário.

    Returns:
        Redirecionamento para a listagem com o resultado da operação.
    """

    form = UserDeleteForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_VALIDATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    try:
        await user_service.delete(
            access_token=session['access_token'],
            user_id=user_id
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/admin/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        if ex.response.status_code == status.HTTP_404_NOT_FOUND:
            return RedirectResponse(
                url='/admin/users?code=USER_NOT_FOUND',
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url=f'/admin/users/{user_id}?code=USER_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url='/admin/users?code=USER_DELETED',
        status_code=status.HTTP_303_SEE_OTHER
    )
