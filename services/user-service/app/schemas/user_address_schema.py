#
# schemas/user_address_schema.py
#

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.user_address import UserAddress


class UserAddressCreateRequest(BaseModel):
    """
    Representa os dados necessários para cadastrar um novo endereço.

    Attributes:
        label: Nome utilizado pelo usuário para identificar o endereço.
        zip_code: CEP do endereço.
        street: Logradouro do endereço.
        number: Número do endereço.
        complement: Complemento do endereço.
        neighborhood: Bairro do endereço.
        city: Cidade do endereço.
        state: Sigla do estado.
        is_default: Indica se o endereço deve ser definido como padrão.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    label: str | None = Field(default=None, max_length=50)
    zip_code: str = Field(min_length=8, max_length=9)
    street: str = Field(min_length=1, max_length=255)
    number: str = Field(min_length=1, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=30)
    is_default: bool = False


class UserAddressResponse(BaseModel):
    """
    Representa um endereço de entrega retornado pela API.

    Attributes:
        id: Identificador único do endereço.
        label: Nome utilizado pelo usuário para identificar o endereço.
        zip_code: CEP do endereço.
        street: Logradouro do endereço.
        number: Número do endereço.
        complement: Complemento do endereço.
        neighborhood: Bairro do endereço.
        city: Cidade do endereço.
        state: Sigla do estado.
        is_default: Indica se este é o endereço padrão do usuário.
        created_at: Data e hora de criação do endereço em UTC.
        updated_at: Data e hora da última atualização do endereço em UTC.
    """

    id: UUID
    label: str | None = None
    zip_code: str
    street: str
    number: str
    complement: str | None = None
    neighborhood: str
    city: str
    state: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, address: UserAddress) -> "UserAddressResponse":
        """
        Cria o schema de resposta a partir do modelo de endereço.

        Args:
            address: Modelo de endereço que será convertido.

        Returns:
            Schema de resposta contendo os dados do endereço.
        """

        return cls(
            id=address.id,
            label=address.label,
            zip_code=address.zip_code,
            street=address.street,
            number=address.number,
            complement=address.complement,
            neighborhood=address.neighborhood,
            city=address.city,
            state=address.state,
            is_default=address.is_default,
            created_at=address.created_at,
            updated_at=address.updated_at
        )


class UserAddressUpdateRequest(BaseModel):
    """
    Representa os dados que podem ser alterados em um endereço de usuário.

    Attributes:
        label: Nome utilizado pelo usuário para identificar o endereço.
        zip_code: CEP do endereço.
        street: Logradouro do endereço.
        number: Número do endereço.
        complement: Complemento do endereço.
        neighborhood: Bairro do endereço.
        city: Cidade do endereço.
        state: Sigla do estado.
        is_default: Indica se o endereço deve ser definido como padrão.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    label: str | None = Field(default=None, max_length=50)
    zip_code: str | None = Field(default=None, min_length=8, max_length=9)
    street: str | None = Field(default=None, min_length=1, max_length=255)
    number: str | None = Field(default=None, min_length=1, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str | None = Field(default=None, min_length=1, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    is_default: bool | None = None