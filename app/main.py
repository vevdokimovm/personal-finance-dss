from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.router import router as api_router
from app.config import settings
from app.database.init_db import init_db


PROJECT_DIR = Path(__file__).resolve().parents[1]
FRONTEND_DIR = PROJECT_DIR / "frontend"
TEMPLATES_DIR = FRONTEND_DIR / "templates"
STATIC_DIR = FRONTEND_DIR / "static"

templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

app = FastAPI(
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.include_router(api_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse, summary="Главная страница приложения")
@app.get("/dashboard", response_class=HTMLResponse, summary="Обзорная панель")
async def read_dashboard(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request, "project_name": settings.PROJECT_NAME},
    )

@app.get("/planning", response_class=HTMLResponse, summary="Планирование и рекомендации СППР")
async def read_planning(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="planning.html",
        context={"request": request, "project_name": settings.PROJECT_NAME},
    )

@app.get("/transactions", response_class=HTMLResponse, summary="Журнал операций")
async def read_transactions(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="transactions.html",
        context={"request": request, "project_name": settings.PROJECT_NAME},
    )

@app.get("/obligations", response_class=HTMLResponse, summary="Обязательства")
async def read_obligations(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="obligations.html",
        context={"request": request, "project_name": settings.PROJECT_NAME},
    )

@app.get("/goals", response_class=HTMLResponse, summary="Цели накопления")
async def read_goals(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="goals.html",
        context={"request": request, "project_name": settings.PROJECT_NAME},
    )

@app.get("/banks", response_class=HTMLResponse, summary="Банковская интеграция")
async def read_banks(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="banks.html",
        context={"request": request, "project_name": settings.PROJECT_NAME},
    )
