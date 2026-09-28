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
    whatsapp: str = Field(min_length=11)
    password: str = Field(min_lenght=8)


class UserResponse(BaseModel):
    """Contrato de saída com dados públicos do usuário."""

    id: UUID
    full_name: str
    email: EmailStr
    confirmed: bool
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
            whatsapp=user.whatsapp,
            created_at=user.created_at,
            updated_at=user.updated_at
        )


class UserSuccessData(BaseModel):
    """
    Representa o bloco `data` de uma resposta de sucesso para operações
    relacionadas ao usuário.

    Este schema segue o padrão JSend adotado pela API, no qual os dados
    de retorno são encapsulados dentro da propriedade `data`.

    Attributes:
        user: Dados do usuário retornado pela operação realizada.
    """

    user: UserResponse


class UserSuccessResponse(BaseModel):
    """
    Representa a resposta de sucesso da API para operações relacionadas
    ao usuário.

    Este schema segue o padrão JSend, retornando:
        - `status`: indicador textual do resultado da operação.
        - `data`: objeto contendo os dados retornados pela operação.

    Attributes:
        status: Indica que a operação foi concluída com sucesso.

        data: Bloco contendo os dados do usuário retornado.
    """

    status: str = 'success'
    data: UserSuccessData


class UserUpdateRequest(BaseModel): 
    """
    Dados permitidos para atualização de um usuário. 
    """ 
    
    model_config = ConfigDict(str_strip_whitespace=True)
    
    full_name: str = Field(min_length=3, max_length=200) 
    email: EmailStr 
    whatsapp: str = Field(min_length=8, max_length=30)