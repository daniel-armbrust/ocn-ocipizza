#
# routes/admin_pizza_routes.py
#

from uuid import UUID

import httpx

from fastapi import APIRouter, Depends, Query, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.dependencies.authentication import get_admin_authenticated_session
from app.dependencies.templates import templates

from app.forms.pizza_forms import (
    PizzaDeleteForm,
    PizzaForm,
    PizzaUpdateForm
)

from app.services.pizza_service import PizzaService, get_pizza_service

router = APIRouter()

#
# GET: /admin/pizzas
#
@router.get(
    '/admin/pizzas',
    response_class=HTMLResponse
)
async def show_admin_pizzas(
    request: Request,
    category: str | None = None,
    available: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=50),
    offset: int = Query(default=0, ge=0),
    session: dict = Depends(get_admin_authenticated_session),
    pizza_service: PizzaService = Depends(get_pizza_service)
) -> Response:
    """
    Exibe o catálogo de pizzas para administração.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        category: Categoria utilizada como filtro opcional.
        available: Disponibilidade utilizada como filtro opcional.
        limit: Quantidade máxima de pizzas exibidas por página.
        offset: Quantidade de pizzas ignoradas antes da página atual.
        session: Sessão administrativa validada pela dependência da rota.
        pizza_service: Serviço responsável pela consulta do catálogo.

    Returns:
        Página HTML contendo a listagem de pizzas.
    """

    paginated_pizzas = await pizza_service.get_all(
        access_token=session['access_token'],
        category=category,
        available=available,

        # Consulta um registro adicional para detectar a próxima página.
        # TODO: Usar metadados de paginação quando o contrato os fornecer.
        limit=limit + 1,
        offset=offset
    )

    has_next_page = len(paginated_pizzas) > limit
    pizzas = paginated_pizzas[:limit]

    return templates.TemplateResponse(
        request=request,
        name='admin/pizzas.html',
        context={
            'pizzas': pizzas,
            'category': category,
            'available': available,
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
# GET: /admin/pizzas/{pizza_id}
#
@router.get(
    '/admin/pizzas/{pizza_id:uuid}',
    response_class=HTMLResponse
)
async def show_admin_pizza(
    request: Request,
    pizza_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    pizza_service: PizzaService = Depends(get_pizza_service)
) -> Response:
    """
    Exibe os detalhes de uma pizza para administração.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        pizza_id: Identificador UUID da pizza consultada.
        session: Sessão administrativa validada pela dependência da rota.
        pizza_service: Serviço responsável pela consulta do catálogo.

    Returns:
        Página HTML contendo os dados detalhados da pizza.
    """

    # Consulta no pizza-service os dados oficiais da pizza selecionada.
    pizza = await pizza_service.get_by_id(
        access_token=session['access_token'],
        pizza_id=pizza_id
    )

    return templates.TemplateResponse(
        request=request,
        name='admin/pizza.html',
        context={
            'pizza': pizza
        }
    )

#
# GET: /admin/pizzas/new
#
@router.get(
    '/admin/pizzas/new',
    response_class=HTMLResponse
)
async def show_new_pizza(
    request: Request,
    _: dict = Depends(get_admin_authenticated_session)
) -> Response:
    """
    Exibe o formulário de criação de pizza.

    Args:
        request: Requisição HTTP recebida pelo admin-service.
        _: Sessão administrativa validada pela dependência da rota.

    Returns:
        Página HTML contendo o formulário de criação.
    """

    return templates.TemplateResponse(
        request=request,
        name='admin/pizza_form.html',
        context={
            'pizza': None,
            'form_action': '/admin/pizzas'
        }
    )

#
# POST: /admin/pizzas
#
@router.post('/admin/pizzas')
@csrf_protect
async def create_admin_pizza(
    request: Request,
    session: dict = Depends(get_admin_authenticated_session),
    service: PizzaService = Depends(get_pizza_service)
) -> RedirectResponse:
    """
    Cria uma pizza usando os dados validados do formulário multipart.

    Args:
        request: Requisição contendo os campos e a imagem da pizza.
        session: Sessão administrativa validada pela dependência da rota.
        service: Serviço responsável pela comunicação com o pizza-service.

    Returns:
        Redirecionamento para o catálogo com o resultado da operação.
    """

    # Converte o multipart recebido pelo navegador em um formulário WTForms.
    # A validação centraliza as regras dos campos textuais e numéricos antes
    # que qualquer chamada seja feita ao pizza-service.
    form = PizzaForm(await request.form())

    # Recupera o arquivo enviado pelo campo `image`; a leitura do conteúdo
    # acontecerá somente depois que os demais campos forem validados.
    image = form.image.data

    if not form.validate() or not hasattr(image, 'read'):
        return RedirectResponse(
            url='/admin/pizzas?code=PIZZA_VALIDATION_ERROR',
            status_code=303
        )

    # Mantém os campos da pizza em um payload separado do arquivo. O cliente
    # HTTP enviará este dicionário como campos multipart do pedido.
    data = {
        name: form[name].data
        for name in (
            'name', 'description', 'category', 'price', 'available'
        )
    }

    # O UploadFile ainda está associado à requisição recebida. A leitura
    # transforma o arquivo em bytes para que possa ser encaminhado ao serviço.
    image_content = await image.read()

    # Um upload sem bytes não representa uma imagem utilizável.
    if not image_content:
        return RedirectResponse(
            url='/admin/pizzas?code=PIZZA_VALIDATION_ERROR',
            status_code=303
        )

    # A tupla segue o formato aceito pelo httpx para upload multipart:
    # nome original, conteúdo binário e tipo informado pelo cliente.
    image_tuple = (image.filename, image_content, image.content_type)

    try:
        await service.create(session['access_token'], data, image_tuple)
    except httpx.HTTPError:
        return RedirectResponse(
            url='/admin/pizzas?code=PIZZA_SERVICE_ERROR',
            status_code=303
        )

    return RedirectResponse(
        url='/admin/pizzas?code=PIZZA_CREATED',
        status_code=303
    )

#
# POST: /admin/pizzas/{pizza_id}/edit
#
@router.post('/admin/pizzas/{pizza_id}/edit')
@csrf_protect
async def update_admin_pizza(
    pizza_id: UUID,
    request: Request,
    session: dict = Depends(get_admin_authenticated_session),
    service: PizzaService = Depends(get_pizza_service)
) -> RedirectResponse:
    """
    Atualiza uma pizza usando o formulário de edição.
    """

    form = PizzaUpdateForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=f'/admin/pizzas/{pizza_id}?code=PIZZA_VALIDATION_ERROR',
            status_code=303
        )

    data = {
        name: form[name].data
        for name in ('name', 'description', 'category', 'price')
        if form[name].data not in (None, '')
    }

    data['available'] = form.available.data
    image = form.image.data
    image_tuple = None

    if hasattr(image, 'read') and image.filename:
        image_tuple = (
            image.filename,
            await image.read(),
            image.content_type
        )

    try:
        await service.update(session['access_token'], pizza_id, data, image_tuple)
    except httpx.HTTPError:
        return RedirectResponse(
            url=f'/admin/pizzas/{pizza_id}?code=PIZZA_SERVICE_ERROR',
            status_code=303
        )

    return RedirectResponse(
        url=f'/admin/pizzas/{pizza_id}?code=PIZZA_UPDATED',
        status_code=303
    )

#
# POST: /admin/pizzas/{pizza_id}/delete
#
@router.post('/admin/pizzas/{pizza_id}/delete')
@csrf_protect
async def delete_admin_pizza(
    request: Request,
    pizza_id: UUID,
    session: dict = Depends(get_admin_authenticated_session),
    service: PizzaService = Depends(get_pizza_service)
) -> RedirectResponse:
    """
    Exclui uma pizza e redireciona para o catálogo.
    """

    form = PizzaDeleteForm(await request.form())

    if not form.validate():
        return RedirectResponse(
            url=f'/admin/pizzas/{pizza_id}?code=PIZZA_VALIDATION_ERROR',
            status_code=303
        )

    try:
        await service.delete(session['access_token'], pizza_id)
    except httpx.HTTPError:
        return RedirectResponse(
            url=f'/admin/pizzas/{pizza_id}?code=PIZZA_SERVICE_ERROR',
            status_code=303
        )

    return RedirectResponse(
        url='/admin/pizzas?code=PIZZA_DELETED',
        status_code=303
    )
