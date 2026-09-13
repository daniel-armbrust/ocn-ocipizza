from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routes import router as page_router


APP_DIR = Path(__file__).resolve().parent

app = FastAPI(title="OCI Pizza - Frontend Service", version="1.0.0")
app.mount("/static", StaticFiles(directory=APP_DIR / "static"), name="static")
app.include_router(page_router)
