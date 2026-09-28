from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.pizza_model import PizzaCategory


class PizzaCreateRequest(BaseModel):
    """Contrato de entrada para cadastro de uma pizza."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: Optional[str] = None
    category: PizzaCategory
    price: float = Field(gt=0)
    image_name: Optional[str] = None
    available: bool = True


class PizzaUpdateRequest(BaseModel):
    """Contrato de entrada para atualização parcial de uma pizza."""

    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    category: Optional[PizzaCategory] = None
    price: Optional[float] = Field(default=None, gt=0)
    image_name: Optional[str] = None
    available: Optional[bool] = None


class PizzaResponseData(BaseModel):
    """Envelope de dados para resposta com uma pizza."""

    pizza: "PizzaResponse"


class PizzaListResponseData(BaseModel):
    """Envelope de dados para resposta com lista de pizzas."""

    pizzas: List["PizzaResponse"]


class PizzaResponse(BaseModel):
    """Contrato de saída com dados públicos de uma pizza."""

    id: int
    name: str
    description: Optional[str] = None
    category: PizzaCategory
    price: float
    image_name: Optional[str] = None
    available: bool
    created_at: datetime
    updated_at: datetime


class JSendSuccess(BaseModel):
    """Representa uma resposta JSend de sucesso."""

    status: str = "success"
    data: Optional[Dict[str, Any]] = None


class JSendFail(BaseModel):
    """Representa uma resposta JSend de falha de validação ou regra."""

    status: str = "fail"
    data: Dict[str, Any]


class JSendError(BaseModel):
    """Representa uma resposta JSend de erro operacional."""

    status: str = "error"
    message: str
