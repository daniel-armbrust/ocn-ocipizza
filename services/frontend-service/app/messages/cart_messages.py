#
# messages/cart_messages.py
#

CART_MESSAGES = {
    'CART_INVALID_ITEMS': {
        'message': (
            'O carrinho possui itens ou quantidades inválidas. Revise o '
            'pedido antes de continuar.'
        ),
        'type': 'warning'
    },
    'CART_CHECKOUT_CONFIRMATION_ERROR': {
        'message': (
            'Não foi possível validar os dados da finalização. Revise o '
            'carrinho e tente novamente.'
        ),
        'type': 'error'
    },
    'CART_PAYMENT_TOKEN_ERROR': {
        'message': (
            'Não foi possível validar os dados do pagamento. Tente finalizar '
            'o pedido novamente.'
        ),
        'type': 'error'
    },
    'CART_CHECKOUT_CHANGED': {
        'message': (
            'O preço, a disponibilidade ou a entrega do pedido mudou. Revise '
            'os dados atualizados antes de continuar.'
        ),
        'type': 'warning'
    },
    'CART_ORDER_CREATION_ERROR': {
        'message': 'Não foi possível criar o pedido. Tente novamente.',
        'type': 'error'
    },
    'CART_PAYMENT_PROCESSING_ERROR': {
        'message': (
            'Não foi possível processar o pagamento. Verifique os dados e '
            'tente novamente.'
        ),
        'type': 'error'
    },
    'CART_QUERY_ERROR': {
        'message': 'Não foi possível exibir os dados do carrinho.',
        'type': 'error'
    }
}
