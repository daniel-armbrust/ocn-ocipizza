#
# messages/user_messages.py
#

USER_MESSAGES = {
    'USER_NOT_FOUND': {
        'message': 'Usuário não encontrado.',
        'type': 'warning'
    },
    'USER_ALREADY_REGISTERED': {
        'message': 'Já existe um usuário cadastrado com este e-mail.',
        'type': 'warning'
    },
    'USER_UPDATE_ERROR': {
        'message': 'Não foi possível atualizar os dados do usuário.',
        'type': 'error'
    },
    'USER_PASSWORD_MISMATCH': {
        'message': 'A senha informada não corresponde à senha atual.',
        'type': 'warning'
    },
    'USER_PASSWORD_UPDATE_ERROR': {
        'message': 'Não foi possível atualizar a senha.',
        'type': 'error'
    },
    'USER_SESSION_REVOCATION_ERROR': {
        'message': 'Não foi possível encerrar a sessão do usuário.',
        'type': 'error'
    },
    'USER_DELETION_ERROR': {
        'message': 'Não foi possível excluir o usuário.',
        'type': 'error'
    },
    'USER_INVALID_CREDENTIALS': {
        'message': 'E-mail ou senha inválidos.',
        'type': 'warning'
    },
    'USER_NOT_CONFIRMED': {
        'message': 'Sua conta ainda não foi confirmada. Verifique o e-mail enviado para concluir o cadastro.',
        'type': 'info'
    },
    'USER_AUTHENTICATION_ERROR': {
        'message': 'Não foi possível realizar a autenticação.',
        'type': 'error'
    },
    'USER_PASSWORD_RESET_REQUEST_ERROR': {
        'message': 'Não foi possível solicitar a redefinição da senha.',
        'type': 'error'
    },
    'USER_INVALID_PASSWORD_RESET_TOKEN': {
        'message': 'O link para redefinição da senha é inválido ou expirou.',
        'type': 'warning'
    },
    'USER_CONFIRMATION_ERROR': {
        'message': 'Não foi possível confirmar o cadastro do usuário.',
        'type': 'error'
    },
    'USER_QUERY_ERROR': {
        'message': 'Não foi possível consultar os dados do usuário.',
        'type': 'error'
    }
}