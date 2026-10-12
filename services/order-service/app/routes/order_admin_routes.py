#
# routes/order_admin_routes.py
#

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.dependencies.authentication import get_current_admin_id

from app.models.order import OrderStatus, PaymentStatus

from app.schemas.jsend_schema import JSendSuccessResponse
from app.schemas.order_schema import OrderResponse, OrderStatusUpdateRequest

from app.responses.jsend import success_response

from app.services.order_service import OrderService, get_order_service

router = APIRouter()

#
# GET: /admin/orders
#
@router.get(
    '/admin/orders',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_orders(
    order_status: OrderStatus | None = Query(default=None),
    payment_status: PaymentStatus | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _: UUID = Depends(get_current_admin_id),
    service: OrderService = Depends(get_order_service)
) -> JSendSuccessResponse:
    """
    Retorna os pedidos disponíveis para acompanhamento administrativo.

    Args:
        order_status: Estado do pedido utilizado como filtro opcional.
        payment_status: Estado do pagamento utilizado como filtro opcional.
        limit: Quantidade máxima de pedidos retornados, limitada a 100.
        offset: Quantidade de pedidos ignorados antes do retorno.
        _: Dependência que valida a autenticação e o privilégio
            administrativo.
        service: Serviço responsável por consultar os pedidos.

    Returns:
        Resposta JSend contendo a página de pedidos correspondente aos
        filtros informados.

    Raises:
        OrderQueryError: Quando ocorrer uma falha durante a consulta.
    """

    orders = service.get_all(
        order_status=order_status,
        payment_status=payment_status,
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
# GET: /admin/orders/{order_id}
#
@router.get(
    '/admin/orders/{order_id}',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def get_order(
    order_id: UUID,
    _: UUID = Depends(get_current_admin_id),
    service: OrderService = Depends(get_order_service)
) -> JSendSuccessResponse:
    """
    Retorna um pedido para acompanhamento administrativo.

    Args:
        order_id: Identificador do pedido solicitado.
        _: Dependência que valida a autenticação e o privilégio
            administrativo.
        service: Serviço responsável por consultar o pedido.

    Returns:
        Resposta JSend contendo o pedido encontrado.

    Raises:
        OrderNotFoundError: Quando o pedido não existir.
        OrderQueryError: Quando ocorrer uma falha durante a consulta.
    """

    order = service.get_by_id_for_admin(order_id=order_id)

    return success_response({
        'order': OrderResponse.from_model(order).model_dump(mode='json')
    })


#
# PATCH: /admin/orders/{order_id}/status
#
@router.patch(
    '/admin/orders/{order_id}/status',
    status_code=status.HTTP_200_OK,
    response_model=JSendSuccessResponse
)
def update_order_status(
    order_id: UUID,
    payload: OrderStatusUpdateRequest,
    _: UUID = Depends(get_current_admin_id),
    service: OrderService = Depends(get_order_service)
) -> JSendSuccessResponse:
    """
    Atualiza administrativamente o status de um pedido.

    Args:
        order_id: Identificador do pedido que será atualizado.
        payload: Novo status validado para o pedido.
        _: Dependência que valida a autenticação e o privilégio
            administrativo.
        service: Serviço responsável por atualizar o pedido.

    Returns:
        Resposta JSend contendo o pedido atualizado.

    Raises:
        OrderNotFoundError: Quando o pedido não existir.
        OrderQueryError: Quando não for possível consultar o pedido.
        OrderUpdateError: Quando não for possível persistir a alteração.
    """

    order = service.update_status_for_admin(
        order_id=order_id,
        order_status=payload.status
    )

    return success_response({
        'order': OrderResponse.from_model(order).model_dump(mode='json')
    })
