#
# exceptions/order_exceptions.py
#


class OrderCreationError(Exception):
    """
    Indica que não foi possível criar um pedido de maneira consistente.
    """
    pass


class OrderIdempotencyConflictError(OrderCreationError):
    """
    Indica a reutilização de uma chave idempotente com conteúdo diferente.
    """
    pass


class OrderQueryError(Exception):
    """
    Indica que não foi possível consultar os pedidos solicitados.
    """
    pass


class OrderNotFoundError(Exception):
    """
    Indica que o pedido solicitado não existe para o usuário autenticado.
    """
    pass


class OrderUpdateError(Exception):
    """
    Indica que não foi possível persistir uma alteração no pedido.
    """
    pass


class OrderDeleteError(Exception):
    """
    Indica que não foi possível remover um pedido.
    """
    pass


class OrderEmailPublishError(Exception):
    """
    Exceção lançada quando não é possível publicar uma notificação 
    de e-mail relacionada ao pedido.
    """
    pass
