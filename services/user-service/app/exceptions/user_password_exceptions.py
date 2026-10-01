#
# exceptions/user_password_exception.py
#

class UserInvalidPasswordError(Exception):
    """
    Exceção lançada quando a senha atual informada pelo usuário
    não corresponde à senha armazenada.
    """
    pass


class UserPasswordMismatchError(Exception):
    """
    Exceção lançada quando a nova senha e sua confirmação possuem
    valores diferentes.
    """
    pass


class UserPasswordResetError(Exception):
    """
    Exceção lançada quando ocorre uma falha durante o processo
    de solicitação ou redefinição da senha de um usuário.
    """
    pass


class UserInvalidPasswordResetTokenError(Exception):
    """
    Exceção lançada quando o token utilizado para redefinição de senha
    é inválido, expirado, já foi utilizado ou foi revogado.
    """
    pass