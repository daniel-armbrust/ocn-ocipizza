#
# exceptions/order_exceptions.py
#


class OrderCreationError(Exception):
    """
    Indica que não foi possível criar um pedido de maneira consistente.
    """


class OrderIdempotencyConflictError(OrderCreationError):
    """
    Indica a reutilização de uma chave idempotente com conteúdo diferente.
    """


class OrderQueryError(Exception):
    """
    Indica que não foi possível consultar os pedidos solicitados.
    """


class OrderNotFoundError(Exception):
    """
    Indica que o pedido solicitado não existe para o usuário autenticado.
    """


class OrderUpdateError(Exception):
    """
    Indica que não foi possível persistir uma alteração no pedido.
    """
