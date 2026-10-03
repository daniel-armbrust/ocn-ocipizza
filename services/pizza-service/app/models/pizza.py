#
# models/pizza.py
#

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum


class PizzaCategory(str, Enum):
    """
    Categorias disponíveis para classificação das pizzas.
    """

    SALGADA = 'salgada'
    VEGETARIANA = 'vegetariana'
    DOCE = 'doce'


@dataclass
class Pizza:
    """
    Representa uma pizza disponível no catálogo da aplicação.

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

    id: UUID | None
    name: str
    description: str
    category: PizzaCategory
    price: Decimal
    image_name: str
    available: bool
    created_at: datetime
    updated_at: datetime