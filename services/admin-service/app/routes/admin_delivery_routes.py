#
# routes/admin_delivery_routes.py
#

import re
from uuid import UUID

import httpx

from fastapi import APIRouter, Depends, Query, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.dependencies.authentication import get_admin_authenticated_session
from app.dependencies.templates import templates

from app.forms.delivery_forms import (
    DeliveryAreaForm,
    DeliveryAreaUpdateForm
)
from app.messages.delivery_service_messages import DELIVERY_MESSAGES

from app.services.delivery_service import DeliveryService, get_delivery_service

router = APIRouter()

#
# GET: /admin/delivery/areas
#
@router.get('/admin/delivery/areas', response_class=HTMLResponse)
async def show_admin_delivery_areas(
    request: Request,
    code: str | None = None,
    active_value: str | None = Query(default=None, alias='active'),
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: dict = Depends(get_admin_authenticated_session),
    delivery_service: DeliveryService = Depends(get_delivery_service)
) -> Response:
    """
    Exibe as áreas de entrega disponíveis para administração.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        active_value: Valor textual do filtro de status enviado pelo
            formulário; valores vazios não aplicam filtro.
        limit: Quantidade máxima de áreas exibidas na página.
        offset: Quantidade de registros ignorados na consulta.
        session: Sessão administrativa validada pela dependência da rota.
        delivery_service: Serviço responsável pela consulta das áreas.

    Returns:
        Página HTML com as áreas de entrega cadastradas.
    """

    # O formulário envia uma string vazia quando o usuário seleciona
    # "Todas as áreas". Nesse caso, a consulta não deve aplicar o filtro.
    active = (
        True if active_value == 'true'
        else False if active_value == 'false'
        else None
    )

    # Consulta um registro adicional para identificar se existe uma próxima
    # página, pois o contrato atual não retorna metadados de paginação.
    delivery_areas = await delivery_service.get_all(
        access_token=session['access_token'],
        active=active,
        limit=limit + 1,
        offset=offset
    )

    message = DELIVERY_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='admin/deliveries.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None,
            'delivery_areas': delivery_areas[:limit],
            'active': active,
            'limit': limit,
            'offset': offset,
            'current_page': (offset // limit) + 1,
            'previous_offset': max(0, offset - limit),
            'next_offset': offset + limit,
            'has_previous_page': offset > 0,
            'has_next_page': len(delivery_areas) > limit
        }
    )

#
# GET: /admin/delivery/areas/new
#
@router.get(
    '/admin/delivery/areas/new',
    response_class=HTMLResponse
)
async def show_new_admin_delivery_area(
    request: Request,
    code: str | None = None,
    _: dict = Depends(get_admin_authenticated_session)
) -> Response:
    """
    Exibe o formulário para criação de uma nova área de entrega.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        code: Código opcional da mensagem exibida no modal global.
        _: Sessão administrativa validada pela dependência da rota.

    Returns:
        Página HTML contendo o formulário de criação.
    """

    message = DELIVERY_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='admin/delivery_form.html',
        context={
            'form_action': '/admin/delivery/areas',
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# GET: /admin/delivery/areas/{delivery_area_id}
#
@router.get(
    '/admin/delivery/areas/{delivery_area_id}',
    response_class=HTMLResponse
)
async def show_admin_delivery_area(
    request: Request,
    delivery_area_id: UUID,
    code: str | None = None,
    session: dict = Depends(get_admin_authenticated_session),
    delivery_service: DeliveryService = Depends(get_delivery_service)
) -> Response:
    """
    Exibe os dados de uma área de entrega para administração.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        delivery_area_id: Identificador UUID da área consultada.
        session: Sessão administrativa validada pela dependência da rota.
        delivery_service: Serviço responsável pela consulta da área.

    Returns:
        Página HTML contendo os dados da área de entrega.
    """

    # Consulta a área pelo serviço para manter a rota desacoplada do cliente
    # HTTP e preservar a separação entre apresentação e integração.
    delivery_area = await delivery_service.get_by_id(
        access_token=session['access_token'],
        delivery_area_id=delivery_area_id
    )

    message = DELIVERY_MESSAGES.get(code) if code else None

    return templates.TemplateResponse(
        request=request,
        name='admin/delivery.html',
        context={
            'delivery_area': delivery_area,
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# POST: /admin/delivery/areas
#
@router.post('/admin/delivery/areas')
@csrf_protect
async def create_admin_delivery_area(
    request: Request,
    session: dict = Depends(get_admin_authenticated_session),
    delivery_service: DeliveryService = Depends(get_delivery_service)
) -> RedirectResponse:
    """
    Cria uma área de entrega a partir do formulário administrativo.

    Args:
        request: Requisição contendo os campos do formulário HTML.
        session: Sessão administrativa validada pela dependência da rota.
        delivery_service: Serviço responsável pela criação da área.

    Returns:
        Redirecionamento para a listagem com o resultado da operação.
    """

    form = DeliveryAreaForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=(
                '/admin/delivery/areas?'
                'code=DELIVERY_VALIDATION_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Remove a máscara do CEP antes de enviar o payload ao delivery-service,
    # que utiliza os oito dígitos como formato canônico.
    payload = {
        'name': form.name.data,
        'zip_code_start': re.sub(r'\D', '', form.zip_code_start.data),
        'zip_code_end': re.sub(r'\D', '', form.zip_code_end.data),
        'delivery_fee': format(form.delivery_fee.data, 'f'),
        'estimated_minutes': form.estimated_minutes.data,
        'active': form.active.data
    }

    try:
        await delivery_service.create(
            access_token=session['access_token'],
            payload=payload
        )
    except httpx.HTTPError:
        return RedirectResponse(
            url=(
                '/admin/delivery/areas?'
                'code=DELIVERY_SERVICE_ERROR'
            ),
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=(
            '/admin/delivery/areas?'
            'code=DELIVERY_CREATED'
        ),
        status_code=status.HTTP_303_SEE_OTHER
    )


# PUT: /admin/delivery/areas/{delivery_area_id}
# POST: /admin/delivery/areas/{delivery_area_id}
@router.put('/admin/delivery/areas/{delivery_area_id}')
@router.post('/admin/delivery/areas/{delivery_area_id}')
@csrf_protect
async def update_admin_delivery_area(
    request: Request,
    delivery_area_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    delivery_service: DeliveryService = Depends(get_delivery_service)
) -> RedirectResponse:
    """Atualiza uma área e redireciona para os seus detalhes."""
    form = DeliveryAreaUpdateForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=f'/admin/delivery/areas/{delivery_area_id}?code=DELIVERY_VALIDATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    payload = {
        key: value for key, value in {
            'name': form.name.data,
            'zip_code_start': (
                re.sub(r'\D', '', form.zip_code_start.data)
                if form.zip_code_start.data else None
            ),
            'zip_code_end': (
                re.sub(r'\D', '', form.zip_code_end.data)
                if form.zip_code_end.data else None
            ),
            'delivery_fee': (
                format(form.delivery_fee.data, 'f')
                if form.delivery_fee.data is not None else None
            ),
            'estimated_minutes': form.estimated_minutes.data,
            'active': form.active.data
        }.items()
        if value is not None and value != ''
    }

    try:
        await delivery_service.update(
            access_token=session['access_token'],
            delivery_area_id=delivery_area_id,
            payload=payload
        )
    except httpx.HTTPError:
        return RedirectResponse(
            url=f'/admin/delivery/areas/{delivery_area_id}?code=DELIVERY_SERVICE_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    return RedirectResponse(
        url=f'/admin/delivery/areas?code=DELIVERY_UPDATED',
        status_code=status.HTTP_303_SEE_OTHER
    )
