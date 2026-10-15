#
# messages/pizza_service_messages.py
#

PIZZA_MESSAGES = {
    'PIZZA_CREATED': {
        'message': 'Pizza criada com sucesso.',
        'type': 'success'
    },
    'PIZZA_UPDATED': {
        'message': 'Pizza atualizada com sucesso.',
        'type': 'success'
    },
    'PIZZA_DELETED': {
        'message': 'Pizza excluída com sucesso.',
        'type': 'success'
    },
    'PIZZA_VALIDATION_ERROR': {
        'message': 'Verifique os dados da pizza e tente novamente.',
        'type': 'warning'
    },
    'PIZZA_SERVICE_ERROR': {
        'message': 'Não foi possível processar a operação da pizza.',
        'type': 'error'
    }
}
