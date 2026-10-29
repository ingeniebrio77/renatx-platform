"""
Punto de entrada principal de `service-api` (FastAPI) — Plataforma Renatx.
Autor: Franco Renato Palavecino (Hamburgo, Alemania)
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, billing, support

app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend modular para la marca personal Renatx (renatx.com) — "
        "Franco Renato Palavecino | Cloud, Linux & IT Training (Hamburg, DE)."
    ),
    version="0.1.0",
)

# Middleware CORS permisivo en entorno local; en producción Traefik unifica el origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Infraestructura y Salud"])
def health_check() -> dict[str, Any]:
    """
    Endpoint de salud y diagnóstico del servicio.
    Usado por el frontend y por monitores de infraestructura.
    """
    return {
        "status": "healthy",
        "brand": "Renatx (renatx.com)",
        "author": settings.owner,
        "environment": settings.env,
        "base_domain": settings.base_domain,
        "database_target": f"{settings.postgres_host}:{settings.postgres_port}/{settings.postgres_db}",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(support.router)
