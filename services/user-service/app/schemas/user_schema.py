#
# schemas/user_schema.py
#

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreateRequest(BaseModel):
    """Contrato para cadastro de novo usuário via API."""

    model_config = ConfigDict(str_strip_whitespace=True)

    full_name: str = Field(min_length=3)
    email: EmailStr
    whatsapp: str = Field(min_length=11, max_length=11)
    password: str = Field(min_lenght=8)


class UserResponse(BaseModel):
    """Contrato de saída com dados públicos do usuário."""

    id: UUID
    full_name: str
    email: EmailStr
    confirmed: bool
    is_admin: bool
    whatsapp: str
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
    token: str