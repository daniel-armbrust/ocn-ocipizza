#
# schemas/user_address_schema.py
#

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.user_address import UserAddress
from app.utils.utils import normalize_zip_code


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
    zip_code: str = Field(pattern=r'^\d{8}$')
    street: str = Field(min_length=1, max_length=255)
    number: str = Field(min_length=1, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str = Field(min_length=1, max_length=100)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=2, max_length=30)
    is_default: bool = False

    @field_validator('zip_code', mode='before')
    @classmethod
    def validate_zip_code(cls, value: str) -> str:
        """
        Normaliza o CEP antes da validação do contrato.

        Args:
            value: CEP recebido com ou sem máscara.

        Returns:
            CEP contendo somente oito dígitos.

        Raises:
            ValueError: Quando o CEP informado for inválido.
        """

        return normalize_zip_code(value)


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
    zip_code: str = Field(pattern=r'^\d{8}$')
    street: str
    number: str
    complement: str | None = None
    neighborhood: str
    city: str
    state: str
    is_default: bool
    created_at: datetime
    updated_at: datetime

    @field_validator('zip_code', mode='before')
    @classmethod
    def validate_zip_code(cls, value: str) -> str:
        """
        Normaliza CEPs legados antes de montar a resposta.

        Args:
            value: CEP recuperado da persistência.

        Returns:
            CEP contendo somente oito dígitos.

        Raises:
            ValueError: Quando o CEP persistido for inválido.
        """

        return normalize_zip_code(value)

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
    zip_code: str | None = Field(default=None, pattern=r'^\d{8}$')
    street: str | None = Field(default=None, min_length=1, max_length=255)
    number: str | None = Field(default=None, min_length=1, max_length=20)
    complement: str | None = Field(default=None, max_length=100)
    neighborhood: str | None = Field(default=None, min_length=1, max_length=100)
    city: str | None = Field(default=None, min_length=1, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=2)
    is_default: bool | None = None

    @field_validator('zip_code', mode='before')
    @classmethod
    def validate_zip_code(cls, value: str | None) -> str | None:
        """
        Normaliza o CEP opcional antes da validação do contrato.

        Args:
            value: CEP recebido com ou sem máscara.

        Returns:
            CEP contendo somente oito dígitos ou `None` quando ausente.

        Raises:
            ValueError: Quando o CEP informado for inválido.
        """

        return normalize_zip_code(value) if value is not None else None
