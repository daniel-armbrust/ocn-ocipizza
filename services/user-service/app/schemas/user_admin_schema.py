#
# schemas/user_admin_schema.py
#

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserAdminCreateRequest(BaseModel):
    """
    Representa os dados necessários para criação administrativa
    de um usuário.

    Attributes:
        full_name: Nome completo do usuário.
        email: Endereço de e-mail do usuário.
        whatsapp: Número de WhatsApp do usuário.
        password: Senha inicial do usuário.
        confirmed: Indica se o endereço de e-mail já deve ser
            considerado confirmado.
        is_admin: Indica se o usuário possuirá privilégios
            administrativos.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    whatsapp: str = Field(min_length=11, max_length=11)
    password: str = Field(min_length=8, max_length=20)
    confirmed: bool = False
    is_admin: bool = False


class UserAdminUpdateRequest(BaseModel):
    """
    Representa os dados permitidos para atualização administrativa
    de um usuário.

    Attributes:
        full_name: Nome completo do usuário.
        email: Endereço de e-mail do usuário.
        whatsapp: Número de WhatsApp do usuário.
        confirmed: Indica se o endereço de e-mail do usuário
            está confirmado.
        is_admin: Indica se o usuário possui privilégios administrativos.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    whatsapp: str = Field(min_length=11, max_length=11)
    confirmed: bool
    is_admin: bool


class UserAdminPasswordUpdateRequest(BaseModel):
    """Representa a definição administrativa da senha de um usuário."""

    new_password: str = Field(min_length=8, max_length=20)
    confirm_new_password: str = Field(min_length=8, max_length=20)
