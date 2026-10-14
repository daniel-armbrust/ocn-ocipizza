#
# exceptions/admin_auth_exceptions.py
#

class AdminAuthenticationError(Exception):
    """
    Exceção lançada quando ocorre uma falha durante a autenticação
    de um usuário no admin-service.
    """
    pass


class AdminAccessDeniedError(Exception):
    """
    Exceção lançada quando o usuário autenticado não possui permissão
    para acessar o admin-service.
    """
    pass
