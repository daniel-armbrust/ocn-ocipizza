#
# schemas/pizza_schema.py
#

from decimal import Decimal
from datetime import datetime
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

from app.models.pizza import PizzaCategory


class PizzaCreateRequest(BaseModel):
    """
    Representa os dados necessários para criação de uma pizza.

    Attributes:
        name: Nome da pizza.
        description: Descrição da pizza.
        price: Preço da pizza.
        image_name: Nome do arquivo de imagem associado à pizza.
        available: Indica se a pizza está disponível para pedidos.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=500)
    category: PizzaCategory
    price: Decimal = Field(gt=0)
    image_name: str = Field(min_length=1, max_length=255)
    available: bool = True


class PizzaUpdateRequest(BaseModel):
    """
    Representa os dados permitidos para atualização de uma pizza.

    Attributes:
        name: Nome da pizza.
        description: Descrição da pizza.
        price: Preço da pizza.
        image_name: Nome do arquivo de imagem associado à pizza.
        available: Indica se a pizza está disponível para pedidos.
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, min_length=1, max_length=500)
    category: PizzaCategory | None = None
    price: Decimal | None = Field(default=None, gt=0, decimal_places=2)
    image_name: str | None = Field(default=None, min_length=1, max_length=255)
    available: bool | None = None


class PizzaResponse(BaseModel):
    """
    Representa os dados de uma pizza retornados pela API.

    Attributes:
        id: Identificador UUID da pizza.
        name: Nome da pizza.
        description: Descrição da pizza.
        category: Categoria da pizza.
        price: Preço da pizza.
        image_name: Nome do arquivo de imagem associado à pizza.
        available: Indica se a pizza está disponível para pedidos.
        created_at: Data e hora de criação da pizza.
        updated_at: Data e hora da última atualização da pizza.
    """

    id: UUID
    name: str
    description: str
    category: PizzaCategory
    price: Decimal
    image_name: str
    image_url: str
    available: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, pizza, image_url: str) -> 'PizzaResponse':
        """
        Cria o schema de resposta a partir do modelo da aplicação.

        Args:
            pizza: Modelo de pizza utilizado pela camada de serviço.

        Returns:
            Schema contendo os dados públicos da pizza.
        """

        return cls(
            id=pizza.id,
            name=pizza.name,
            description=pizza.description,
            category=pizza.category,
            price=pizza.price,
            image_name=pizza.image_name,
            image_url=image_url,
            available=pizza.available,
            created_at=pizza.created_at,
            updated_at=pizza.updated_at
        )
  