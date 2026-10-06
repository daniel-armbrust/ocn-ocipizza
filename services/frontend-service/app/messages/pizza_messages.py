#
# messages/pizza_messages.py
#

PIZZA_MESSAGES = {
    'PIZZA_NOT_FOUND': {
        'message': 'Pizza não encontrada.',
        'type': 'warning'
    },
    'PIZZA_QUERY_ERROR': {
        'message': 'Não foi possível consultar o catálogo de pizzas.',
        'type': 'error'
    },
    'PIZZA_CREATION_ERROR': {
        'message': 'Não foi possível cadastrar a pizza.',
        'type': 'error'
    },
    'PIZZA_EMPTY_IMAGE': {
        'message': 'A imagem da pizza não foi informada.',
        'type': 'warning'
    },
    'PIZZA_INVALID_IMAGE_CONTENT_TYPE': {
        'message': 'O formato da imagem selecionada não é suportado.',
        'type': 'warning'
    },
    'PIZZA_UPDATE_ERROR': {
        'message': 'Não foi possível atualizar os dados da pizza.',
        'type': 'error'
    },
    'PIZZA_DELETION_ERROR': {
        'message': 'Não foi possível excluir a pizza.',
        'type': 'error'
    }
}