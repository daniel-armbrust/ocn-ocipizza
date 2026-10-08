#
# exceptions/user_address_exceptions.py
#

class UserAddressNotFoundError(Exception):
    """
    Exceção lançada quando um endereço de usuário não é encontrado.
    """
    pass


class UserAddressLimitExceededError(Exception):
    """
    Exceção lançada quando o limite de endereços é atingido.
    """
    pass