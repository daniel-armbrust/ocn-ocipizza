from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class PizzaCategory(str, Enum):
    TRADITIONAL = "tradicional"
    VEGETARIAN = "vegetariana"
    SWEET = "doce"


class Pizza(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    id: int = Field(default=0)
    name: str
    description: Optional[str] = None
    category: PizzaCategory
    price: float
    image_name: Optional[str] = None
    available: bool = True
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
