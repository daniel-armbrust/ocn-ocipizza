#
# messages/user_service_messages.py
#

USER_MESSAGES = {
    'USER_AUTHENTICATION_SUCCESS': {
        'message': 'Usuário autenticado com sucesso.',
        'type': 'success'
    },
    'USER_NOT_FOUND': {
        'message': 'Usuário não encontrado.',
        'type': 'warning'
    },
    'USER_INVALID_CREDENTIALS': {
        'message': 'E-mail ou senha inválidos.',
        'type': 'warning'
    },
    'USER_AUTHENTICATION_ERROR': {
        'message': 'Não foi possível realizar a autenticação.',
        'type': 'error'
    },
    'USER_AUTHENTICATION_INVALID': {
        'message': 'Informe um e-mail e uma senha válidos.',
        'type': 'error'
    },
    'USER_LOGIN_REQUIRED': {
        'message': 'É necessário realizar login para continuar.',
        'type': 'warning'
    }
}