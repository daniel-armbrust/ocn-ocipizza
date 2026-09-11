from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.pizza_model import PizzaCategory


class PizzaCreateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    description: Optional[str] = None
    category: PizzaCategory
    price: float = Field(gt=0)
    image_name: Optional[str] = None
    available: bool = True


class PizzaUpdateRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    category: Optional[PizzaCategory] = None
    price: Optional[float] = Field(default=None, gt=0)
    image_name: Optional[str] = None
    available: Optional[bool] = None


class PizzaResponseData(BaseModel):
    pizza: "PizzaResponse"


class PizzaListResponseData(BaseModel):
    pizzas: List["PizzaResponse"]


class PizzaResponse(BaseModel):
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
    status: str = "success"
    data: Optional[Dict[str, Any]] = None


class JSendFail(BaseModel):
    status: str = "fail"
    data: Dict[str, Any]


class JSendError(BaseModel):
    status: str = "error"
    message: str
