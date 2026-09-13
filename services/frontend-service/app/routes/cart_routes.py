from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.routes.templates import templates


router = APIRouter()


@router.get("/cart", response_class=HTMLResponse)
async def cart(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "cart.html",
        {},
    )
