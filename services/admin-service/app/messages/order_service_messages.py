#
# messages/order_service_messages.py
#

ORDER_MESSAGES = {
    'ORDER_DELETED': {
        'message': 'Pedido excluído com sucesso.',
        'type': 'success'
    },
    'ORDER_SERVICE_DELETE_ERROR': {
        'message': 'Não foi possível excluir o pedido.',
        'type': 'error'
    },
    'ORDER_STATUS_UPDATED': {
        'message': 'Status do pedido atualizado com sucesso.',
        'type': 'success'
    },
    'ORDER_SERVICE_IDEMPOTENCY_CONFLICT': {
        'message': 'O pedido informado entra em conflito com outro pedido.',
        'type': 'warning'
    },
    'ORDER_SERVICE_CREATION_ERROR': {
        'message': 'Não foi possível criar o pedido.',
        'type': 'error'
    },
    'ORDER_SERVICE_QUERY_ERROR': {
        'message': 'Não foi possível consultar os pedidos.',
        'type': 'error'
    },
    'ORDER_SERVICE_ORDER_NOT_FOUND': {
        'message': 'Pedido não encontrado.',
        'type': 'warning'
    },
    'ORDER_SERVICE_UPDATE_ERROR': {
        'message': 'Não foi possível atualizar o pedido.',
        'type': 'error'
    },
    'ORDER_SERVICE_VALIDATION_ERROR': {
        'message': 'Verifique os dados do pedido e tente novamente.',
        'type': 'warning'
    },
    'ORDER_SERVICE_AUTHENTICATION_ERROR': {
        'message': 'Não foi possível autenticar a consulta de pedidos.',
        'type': 'error'
    },
    'ORDER_SERVICE_AUTHORIZATION_ERROR': {
        'message': 'Você não possui permissão para realizar esta operação.',
        'type': 'warning'
    },
    'ORDER_SERVICE_HTTP_ERROR': {
        'message': 'Não foi possível processar a operação do pedido.',
        'type': 'error'
    },
    'ORDER_SERVICE_INTERNAL_SERVER_ERROR': {
        'message': 'Ocorreu um erro interno ao processar o pedido.',
        'type': 'error'
    }
}
