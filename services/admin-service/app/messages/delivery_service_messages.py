#
# messages/delivery_service_messages.py
#

DELIVERY_MESSAGES = {
    'DELIVERY_CREATED': {
        'message': 'Área de entrega criada com sucesso.',
        'type': 'success'
    },
    'DELIVERY_UPDATED': {
        'message': 'Área de entrega atualizada com sucesso.',
        'type': 'success'
    },
    'DELIVERY_DELETED': {
        'message': 'Área de entrega excluída com sucesso.',
        'type': 'success'
    },
    'DELIVERY_VALIDATION_ERROR': {
        'message': 'Revise os dados da área de entrega.',
        'type': 'error'
    },
    'DELIVERY_SERVICE_ERROR': {
        'message': 'Não foi possível concluir a operação de entrega.',
        'type': 'error'
    }
}
