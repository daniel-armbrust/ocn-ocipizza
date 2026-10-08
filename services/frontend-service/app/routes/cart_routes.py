#
# routes/cart_routes.py
#

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.dependencies.templates import templates

router = APIRouter()

#
# GET: /cart
#
@router.get('/cart', response_class=HTMLResponse)
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
