#
# models/user_authentication_tokens.py
#

from dataclasses import dataclass


@dataclass
class UserAuthenticationTokens:
    """
    Representa os tokens gerados durante a autenticação de um usuário.

    Esta classe é utilizada internamente pela aplicação para transportar
    os tokens gerados pelo processo de autenticação entre a camada de
    serviço e a camada responsável pela resposta HTTP.

    Attributes:
        access_token: JWT utilizado para autenticar as requisições
            realizadas aos serviços da aplicação.
        refresh_token: Token utilizado para obter um novo access token
            sem exigir novamente as credenciais do usuário.
        expires_in: Tempo de validade do access token, em segundos.
    """

    access_token: str
    refresh_token: str
    expires_in: int