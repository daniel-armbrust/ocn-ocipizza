#
# models/user_address.py
#

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class UserAddress(BaseModel):
    """
    Representa um endereço pertencente a um usuário.

    Attributes:
        id: Identificador único do endereço.
        user_id: Identificador único do usuário proprietário do endereço.
        label: Nome utilizado para identificar o endereço.
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
    user_id: UUID
    label: str | None = None
    zip_code: str
    street: str
    number: str
    complement: str | None = None
    neighborhood: str
    city: str
    state: str
    is_default: bool = False
    created_at: datetime
    updated_at: datetime