#
# routes/cart_routes.py
#

import httpx

from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.dependencies.authentication import get_authenticated_session

from app.exceptions.checkout_exceptions import CheckoutChangedError
from app.forms.cart_forms import (
    CartCheckoutConfirmationForm,
    CartCheckoutForm
)
from app.messages.cart_messages import CART_MESSAGES
from app.services.checkout_service import CheckoutService, get_checkout_service

from app.dependencies.templates import templates

router = APIRouter()

CHECKOUT_ITEMS_SESSION_KEY = 'checkout_items'

#
# GET: /cart
#
@router.get(
        '/cart',
        response_class=HTMLResponse
)
async def show_cart(
    request: Request,
    code: str | None = None
) -> HTMLResponse:
    """
    Exibe a página do carrinho de compras.

    Os itens do carrinho são armazenados no localStorage do navegador
    e carregados pelo JavaScript da página.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        code: Código funcional opcional que identifica a mensagem exibida.

    Returns:
        Página HTML do carrinho de compras.
    """

    message = CART_MESSAGES.get(
        code,
        {
            'message': 'Não foi possível processar a operação solicitada.',
            'type': 'error'
        }
    ) if code else None

    return templates.TemplateResponse(
        request=request,
        name='cart/cart.html',
        context={
            'message': message['message'] if message else None,
            'type': message['type'] if message else None
        }
    )

#
# GET: /cart/checkout
#
@router.get(
    '/cart/checkout',
    response_class=HTMLResponse
)
async def show_checkout(
    request: Request,
    session=Depends(get_authenticated_session),
    checkout_service: CheckoutService = Depends(get_checkout_service)
) -> Response:
    """
    Exibe o checkout preparado com os dados atuais dos microsserviços.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.
        session: Sessão autenticada mantida pelo frontend-service.
        checkout_service: Serviço responsável por preparar o checkout.

    Returns:
        Página HTML do checkout ou redirecionamento para o carrinho quando
        não existem itens válidos preparados na sessão.

    Raises:
        httpx.HTTPStatusError: Caso um microsserviço rejeite uma consulta.
        httpx.RequestError: Caso um microsserviço esteja indisponível.
    """

    submitted_items = request.session.get(CHECKOUT_ITEMS_SESSION_KEY)

    if not isinstance(submitted_items, list) or not submitted_items:
        return RedirectResponse(
            url='/cart?code=CART_INVALID_ITEMS',
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Falhas HTTP e de comunicação são tratadas pelos handlers globais.
    checkout = await checkout_service.prepare_checkout(
        access_token=session['access_token'],
        items=submitted_items
    )

    checkout['idempotency_key'] = str(uuid4())

    return templates.TemplateResponse(
        request=request,
        name='cart/checkout.html',
        context=checkout
    )

#
# POST: /cart/checkout
#
@router.post('/cart/checkout')
@csrf_protect
async def prepare_checkout(
    request: Request,
    session=Depends(get_authenticated_session)
) -> RedirectResponse:
    """
    Valida os itens enviados pelo carrinho e inicia a etapa de checkout.

    Args:
        request: Requisição HTTP recebida com os itens do carrinho.
        session: Sessão autenticada mantida pelo frontend-service.

    Returns:
        Redirecionamento para o checkout ou para o carrinho quando os itens
        submetidos forem inválidos.
    """

    # Valida apenas os identificadores e as quantidades enviados pelo
    # navegador. Nomes, disponibilidade e preços do localStorage não são
    # considerados confiáveis para a preparação do pedido.
    form = CartCheckoutForm(await request.form())

    if not form.validate():
        # Retorna ao carrinho quando a carga não contiver ao menos um item
        # válido, evitando consultas desnecessárias aos demais serviços.
        return RedirectResponse(
            url='/cart?code=CART_INVALID_ITEMS',
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Converte os campos aninhados do WTForms em uma estrutura simples que
    # será associada aos dados oficiais retornados pelo pizza-service.
    submitted_items = [
        {
            'pizza_id': item.form.pizza_id.data,
            'quantity': item.form.quantity.data
        }
        for item in form.items.entries
    ]

    # A sessão assinada mantém somente IDs e quantidades entre o POST e o GET.
    # Nomes, preços e disponibilidade continuam sendo consultados novamente.
    request.session[CHECKOUT_ITEMS_SESSION_KEY] = submitted_items

    return RedirectResponse(
        url='/cart/checkout',
        status_code=status.HTTP_303_SEE_OTHER
    )

#
# POST: /cart/checkout/confirm
#
@router.post('/cart/checkout/confirm')
@csrf_protect
async def confirm_checkout(
    request: Request,
    session=Depends(get_authenticated_session),
    checkout_service: CheckoutService = Depends(get_checkout_service)
) -> Response:
    """
    Confirma que o checkout não mudou e cria o pedido.

    Args:
        request: Requisição contendo o checkout e o token de pagamento.
        session: Sessão autenticada mantida pelo frontend-service.
        checkout_service: Serviço responsável por revalidar o checkout.

    Returns:
        Redirecionamento para o cardápio após a criação do pedido ou para o
        carrinho quando os dados forem inválidos ou tiverem mudado.
    """

    form = CartCheckoutConfirmationForm(await request.form())

    if not form.validate():
        code = (
            'CART_PAYMENT_TOKEN_ERROR'
            if form.payment_token.errors
            else 'CART_CHECKOUT_CONFIRMATION_ERROR'
        )

        return RedirectResponse(
            url=f'/cart?code={code}',
            status_code=status.HTTP_303_SEE_OTHER
        )

    # `submitted_checkout` representa o estado do checkout que foi apresentado
    # ao usuário e devolvido pelo formulário por meio de campos ocultos. Esses
    # valores não são considerados confiáveis nem usados diretamente para criar
    # o pedido: o CheckoutService consulta novamente os serviços responsáveis e
    # compara endereço, itens, preços e totais antes de autorizar a continuidade.
    submitted_checkout = {
        'address_id': form.address_id.data,
        'items': [
            {
                'pizza_id': item.form.pizza_id.data,
                'quantity': item.form.quantity.data,
                'unit_price': item.form.unit_price.data
            }
            for item in form.items.entries
        ],
        'subtotal': form.subtotal.data,
        'delivery_fee': form.delivery_fee.data,
        'total': form.total.data
    }

    try:
        await checkout_service.confirm_checkout(
            access_token=session['access_token'],
            submitted_checkout=submitted_checkout,
            payment_token=form.payment_token.data,
            idempotency_key=form.idempotency_key.data
        )
    except CheckoutChangedError:
        # Retorna ao carrinho para que preços, disponibilidade e entrega sejam
        # apresentados novamente antes de uma nova tentativa de pagamento.
        return RedirectResponse(
            url='/cart?code=CART_CHECKOUT_CHANGED',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError:
        return RedirectResponse(
            url='/cart?code=CART_CHECKOUT_CONFIRMATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.HTTPStatusError as ex:
        if ex.response.status_code == status.HTTP_401_UNAUTHORIZED:
            return RedirectResponse(
                url='/users/login?code=USER_LOGIN_REQUIRED',
                status_code=status.HTTP_303_SEE_OTHER
            )

        return RedirectResponse(
            url='/cart?code=CART_ORDER_CREATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )
    except httpx.RequestError:
        return RedirectResponse(
            url='/cart?code=CART_ORDER_CREATION_ERROR',
            status_code=status.HTTP_303_SEE_OTHER
        )

    request.session.pop(CHECKOUT_ITEMS_SESSION_KEY, None)

    return RedirectResponse(
        url='/users/profile/orders?code=CART_ORDER_SUCCESSFULLY_CREATED',
        status_code=status.HTTP_303_SEE_OTHER
    )
