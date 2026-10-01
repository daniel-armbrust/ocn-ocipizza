#
# schemas/user_password_schema.py
#

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserPasswordUpdateRequest(BaseModel):
    """
    Dados necessários para alteração da senha do usuário autenticado.

    A senha atual é utilizada para validar a identidade do usuário.
    A nova senha deve ser informada duas vezes para evitar erros
    de digitação.

    Attributes:
        current_password: Senha atual utilizada para validação do
            usuário.
        new_password: Nova senha desejada pelo usuário.
        confirm_new_password: Confirmação da nova senha informada
             pelo usuário.
    """

    current_password: str
    new_password: str
    confirm_new_password: str


class UserPasswordResetRequest(BaseModel):
    """
    Representa a solicitação de recuperação de senha.

    Este schema é utilizado quando o usuário informa seu e-mail para
    iniciar o processo de redefinição de senha. Após a solicitação,
    o serviço gera um token temporário e envia uma mensagem para o
    `notification-service` responsável pelo envio da comunicação ao
    usuário.

    Attributes:
        email: Endereço de e-mail associado à conta do usuário.
    """

    email: EmailStr


class UserPasswordResetConfirmRequest(BaseModel):
    """
    Representa a confirmação da redefinição de senha.

    Este schema é utilizado após o usuário receber o token de
    recuperação enviado pelo processo de reset de senha. O token é
    validado e, caso seja válido, a nova senha informada é aplicada
    ao usuário.

    A nova senha deve ser informada duas vezes para reduzir erros de
    digitação durante o processo de alteração.

    Attributes:
        token: Token temporário utilizado para validar a solicitação
            de redefinição de senha.
        new_password: Nova senha desejada pelo usuário.
        confirm_new_password: Confirmação da nova senha informado 
            pelo usuário.
    """

    token: str
    new_password: str
    confirm_new_password: str