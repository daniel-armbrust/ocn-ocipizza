#
# routes/order_routes.py
#

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.authentication import get_current_user_id

from app.responses.jsend import success_response

from app.schemas.jsend_schema import JSendSuccessResponse
from app.schemas.order_schema import OrderCreateRequest, OrderResponse

from app.services.order_service import OrderService, get_order_service

router = APIRouter()

#
# GET: /orders
#
@router.get(
    '/orders',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_orders(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user_id: UUID = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> JSendSuccessResponse:
    """
    Retorna os pedidos pertencentes ao usuário autenticado.

    Args:
        limit: Quantidade máxima de pedidos retornados, limitada a 100.
        offset: Quantidade de pedidos ignorados antes do retorno.
        user_id: Identificador extraído do JWT do usuário autenticado.
        service: Serviço responsável por consultar os pedidos.

    Returns:
        Resposta JSend contendo a página de pedidos do usuário.

    Raises:
        OrderQueryError: Quando ocorrer uma falha durante a consulta.
    """

    orders = service.get_by_user_id(
        user_id=user_id,
        limit=limit,
        offset=offset
    )

    return success_response({
        'orders': [
            OrderResponse.from_model(order).model_dump(mode='json')
            for order in orders
        ]
    })


#
# GET: /orders/{order_id}
#
@router.get(
    '/orders/{order_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_order(
    order_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> JSendSuccessResponse:
    """
    Retorna um pedido pertencente ao usuário autenticado.

    Args:
        order_id: Identificador do pedido solicitado.
        user_id: Identificador extraído do JWT do usuário autenticado.
        service: Serviço responsável por consultar o pedido.

    Returns:
        Resposta JSend contendo o pedido encontrado.

    Raises:
        OrderNotFoundError: Quando o pedido não existir para o usuário.
        OrderQueryError: Quando ocorrer uma falha durante a consulta.
    """

    order = service.get_by_id(user_id=user_id, order_id=order_id)

    return success_response({
        'order': OrderResponse.from_model(order).model_dump(mode='json')
    })


#
# POST: /orders
#
@router.post(
    '/orders',
    status_code=status.HTTP_201_CREATED,
    response_model=JSendSuccessResponse
)
def create_order(
    payload: OrderCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    service: OrderService = Depends(get_order_service)
) -> JSendSuccessResponse:
    """
    Cria um pedido para o usuário autenticado.

    O identificador do proprietário não é aceito no corpo da requisição. Ele
    é obtido do claim `sub` do JWT para impedir que um usuário crie pedidos em
    nome de outra pessoa.

    Args:
        payload: Snapshots, itens, valores e chave de idempotência validados.
        user_id: Identificador extraído do JWT do usuário autenticado.
        service: Serviço responsável pelas regras de criação do pedido.

    Returns:
        Resposta JSend contendo o pedido criado ou anteriormente associado à
        mesma chave de idempotência.

    Raises:
        OrderCreationError: Quando não for possível criar ou recuperar o
            pedido de maneira idempotente.
    """

    # A rota apenas coordena o contrato HTTP. A criação do domínio, a
    # idempotência e a persistência pertencem à camada de serviço.
    order = service.create(
        user_id=user_id,
        payload=payload
    )

    # Converte o domínio antes de montar a resposta para evitar que detalhes
    # internos da persistência sejam expostos pela API.
    response = OrderResponse.from_model(order)

    return success_response({
        'order': response.model_dump(mode='json')
    })
