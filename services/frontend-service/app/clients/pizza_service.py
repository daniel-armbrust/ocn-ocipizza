from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from app.config.settings import Settings


@dataclass(frozen=True)
class PizzaCatalogResult:
    pizzas: List[Dict[str, Any]]
    error_message: Optional[str] = None

    @property
    def is_available(self) -> bool:
        return self.error_message is None


class PizzaServiceClient:
    def __init__(self, settings: Settings) -> None:
        self.base_url = settings.pizza_service_url.rstrip("/")
        self.image_base_url = settings.pizza_image_base_url.rstrip("/")
        self.timeout = settings.request_timeout

    async def list_pizzas(self) -> PizzaCatalogResult:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/pizzas")
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError):
            return PizzaCatalogResult(
                pizzas=[],
                error_message="Nao foi possivel carregar o catalogo agora.",
            )

        pizzas = self._extract_pizzas(payload)

        if pizzas is None:
            return PizzaCatalogResult(
                pizzas=[],
                error_message="O catalogo retornou uma resposta inesperada.",
            )

        return PizzaCatalogResult(
            pizzas=[self._with_image_url(pizza) for pizza in pizzas],
        )

    def _extract_pizzas(self, payload: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
        if payload.get("status") != "success":
            return None

        data = payload.get("data")

        if not isinstance(data, dict):
            return None

        pizzas = data.get("pizzas")

        if not isinstance(pizzas, list):
            return None

        return [pizza for pizza in pizzas if isinstance(pizza, dict)]

    def _with_image_url(self, pizza: Dict[str, Any]) -> Dict[str, Any]:
        image_name = pizza.get("image_name")

        if not isinstance(image_name, str) or image_name == "":
            return pizza

        return {
            **pizza,
            "image_url": f"{self.image_base_url}/{quote(image_name)}",
        }
