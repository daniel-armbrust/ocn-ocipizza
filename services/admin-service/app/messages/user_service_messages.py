#
# messages/user_service_messages.py
#

USER_MESSAGES = {
    'USER_CREATED': {
        'message': 'Usuário criado com sucesso.',
        'type': 'success'
    },
    'USER_UPDATED': {
        'message': 'Usuário atualizado com sucesso.',
        'type': 'success'
    },
    'USER_DELETED': {
        'message': 'Usuário excluído com sucesso.',
        'type': 'success'
    },
    'USER_VALIDATION_ERROR': {
        'message': 'Revise os dados informados para o usuário.',
        'type': 'error'
    },
    'USER_SERVICE_ERROR': {
        'message': 'Não foi possível concluir a operação de usuário.',
        'type': 'error'
    },
    'USER_ALREADY_REGISTERED': {
        'message': 'Já existe um usuário cadastrado com estes dados.',
        'type': 'warning'
    },
    'USER_VALIDATION_ERROR': {
        'message': 'Revise os campos informados e tente novamente.',
        'type': 'error'
    },
    'USER_AUTHENTICATION_SUCCESS': {
        'message': 'Usuário autenticado com sucesso.',
        'type': 'success'
    },
    'USER_LOGOUT_SUCCESS': {
        'message': 'Sessão encerrada com sucesso.',
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
