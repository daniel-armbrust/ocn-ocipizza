#
# schemas/user_authentication_schema.py
#

from pydantic import BaseModel, EmailStr, Field


class UserLoginRequest(BaseModel):
    """
    Representa os dados necessários para autenticação de um usuário.

    Attributes:
        email: Endereço de e-mail utilizado para identificar o usuário.
        password: Senha informada para autenticação.
    """

    email: EmailStr
    password: str = Field(min_length=11, max_length=11)


class UserRefreshTokenRequest(BaseModel):
    """
    Representa os dados necessários para renovação do access token.

    O refresh token é utilizado para solicitar um novo access token
    sem exigir novamente as credenciais do usuário.

    Attributes:
        refresh_token: Token utilizado para renovação da sessão.
    """

    refresh_token: str = Field(min_length=20, max_length=255)


class UserLogoutRequest(BaseModel):
    """
    Representa os dados necessários para encerrar uma sessão.

    O refresh token informado será localizado e revogado para impedir
    sua utilização em novas solicitações de access token.

    Attributes:
        refresh_token: Token associado à sessão que será encerrada.
    """

    refresh_token: str = Field(min_length=20, max_length=255)


class UserTokenResponse(BaseModel):
    """
    Representa os tokens retornados após uma autenticação bem-sucedida.

    Attributes:
        access_token: JWT utilizado para autenticar requisições aos
            serviços da aplicação.
        refresh_token: Token utilizado para obter um novo access token.
        token_type: Tipo do token utilizado no cabeçalho Authorization.
        expires_in: Tempo de validade do access token, em segundos.
    """

    access_token: str = Field(min_length=20, max_length=255)
    refresh_token: str = Field(min_length=20, max_length=255)
    token_type: str = 'Bearer'
    expires_in: int