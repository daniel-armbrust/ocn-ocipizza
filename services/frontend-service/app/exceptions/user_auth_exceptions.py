#
# exceptions/user_auth_exceptions.py
#

class AuthenticationRequiredError(Exception):
    """
    Indica que a página exige uma sessão autenticada.
    """
    pass