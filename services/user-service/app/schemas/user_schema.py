#
# schemas/user_schema.py
#

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateRequest(BaseModel):
    """
    Representa os dados necessários para cadastrar um novo usuário.

    Attributes:
        full_name: Nome completo do usuário.
        email: Endereço de e-mail utilizado para identificação e comunicação.
        whatsapp: Número de WhatsApp do usuário.
        password: Senha informada pelo usuário para criação da conta.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    whatsapp: str = Field(min_length=11, max_length=11)
    password: str = Field(min_length=8, max_length=20)


class UserResponse(BaseModel):
    """
    Representa os dados de um usuário retornados pela API.

    Attributes:
        id: Identificador único do usuário.
        full_name: Nome completo do usuário.
        email: Endereço de e-mail cadastrado.
        whatsapp: Número de WhatsApp cadastrado.
        confirmed: Indica se o endereço de e-mail do usuário foi confirmado.
        created_at: Data e hora de criação do usuário em UTC.
        updated_at: Data e hora da última atualização do usuário em UTC.
    """

    id: UUID
    full_name: str = Field(min_length=3, max_length=255)
    email: EmailStr
    confirmed: bool
    is_admin: bool
    whatsapp: str = Field(min_length=11, max_length=11)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, user):
        """
        Cria resposta pública a partir do modelo interno de usuário.

        Args:
            user: Modelo interno de usuário retornado pela camada de domínio.

        Returns:
            Instância de `UserResponse` com apenas dados públicos.
        """

        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            confirmed=user.confirmed,
            is_admin=user.is_admin,
            whatsapp=user.whatsapp,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class UserUpdateRequest(BaseModel): 
    """
    Dados permitidos para atualização do usuário.

    Attributes:
        whatsapp: Número de WhatsApp do usuário utilizado para contato
            e comunicação.
    """ 
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    whatsapp: str = Field(min_length=11, max_length=11)


class UserConfirmationRequest(BaseModel):
    """
    Representa os dados necessários para confirmação do cadastro
    de um usuário.

    Attributes:
        email: Endereço de e-mail associado ao cadastro.
        token: Token utilizado para validar a confirmação do usuário.
    """

    email: EmailStr
    token: str = Field(min_length=20, max_length=255)