from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.routes.templates import templates


router = APIRouter()


@router.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request,
        "checkout.html",
        {},
    )
