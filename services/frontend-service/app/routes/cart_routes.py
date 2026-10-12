#
# routes/cart_routes.py
#

from uuid import uuid4

from fastapi import APIRouter, Depends, Request, status, Response
from fastapi.responses import HTMLResponse, RedirectResponse

from starlette_wtf import csrf_protect

from app.dependencies.authentication import get_authenticated_session

from app.dependencies.templates import templates
from app.forms.cart_forms import CartCheckoutForm
from app.services.checkout_service import CheckoutService, get_checkout_service

router = APIRouter()

#
# GET: /cart
#
@router.get(
        '/cart',
        response_class=HTMLResponse
)
async def show_cart(request: Request) -> HTMLResponse:
    """
    Exibe a página do carrinho de compras.

    Os itens do carrinho são armazenados no localStorage do navegador
    e carregados pelo JavaScript da página.

    Args:
        request: Requisição HTTP recebida pelo frontend-service.

    Returns:
        Página HTML do carrinho de compras.
    """

    return templates.TemplateResponse(
        request=request,
        name='cart/cart.html',
        context={}
    )

#
# POST: /cart/checkout
#
@router.post(
        '/cart/checkout',
        response_class=HTMLResponse
)
@csrf_protect
async def show_checkout(
    request: Request,
    session=Depends(get_authenticated_session),
    checkout_service: CheckoutService = Depends(get_checkout_service)
) -> Response:
    """
    Exibe a etapa de pagamento do pedido.

    Valida novamente as pizzas e seus preços, obtém o endereço principal
    do usuário e consulta a disponibilidade da entrega antes de apresentar
    o formulário de pagamento.

    Args:
        request: Requisição HTTP recebida com os itens do carrinho.
        session: Sessão autenticada mantida pelo frontend-service.
        checkout_service: Serviço responsável por preparar o checkout.

    Returns:
        Página HTML do checkout ou redirecionamento para o carrinho quando
        os itens submetidos forem inválidos.
    """

    # Valida apenas os identificadores e as quantidades enviados pelo
    # navegador. Nomes, disponibilidade e preços do localStorage não são
    # considerados confiáveis para a preparação do pedido.
    form = CartCheckoutForm(await request.form())

    if not form.validate():
        # Retorna ao carrinho quando a carga não contiver ao menos um item
        # válido, evitando consultas desnecessárias aos demais serviços.
        return RedirectResponse(
            url='/cart',
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

    # A rota delega toda a orquestração e os cálculos ao serviço para que a
    # futura confirmação possa executar exatamente as mesmas regras.
    checkout = await checkout_service.prepare_checkout(
        access_token=session['access_token'],
        items=submitted_items
    )

    # A chave nasce junto com a apresentação do checkout e será reutilizada
    # em todas as tentativas de confirmar este mesmo formulário. O controle
    # definitivo contra pedidos duplicados pertencerá ao order-service.
    checkout['idempotency_key'] = str(uuid4())

    return templates.TemplateResponse(
        request=request,
        name='cart/checkout.html',
        context=checkout
    )

#
# POST: /cart/checkout/confirm
#
