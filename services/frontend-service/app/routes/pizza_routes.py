from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.clients.pizza_service import PizzaServiceClient
from app.config.settings import get_settings
from app.routes.templates import templates


router = APIRouter()


@router.get("/pizzas", response_class=HTMLResponse)
async def pizzas(request: Request) -> HTMLResponse:
    settings = get_settings()
    catalog = await PizzaServiceClient(settings).list_pizzas()

    return templates.TemplateResponse(
        request,
        "pizzas.html",
        {
            "catalog": catalog,
            "pizzas": catalog.pizzas,
        },
    )
