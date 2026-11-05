"""
Punto de entrada principal de `service-api` (FastAPI) — Plataforma Renatx.
Autor: Franco Renato Palavecino (Hamburgo, Alemania)
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import auth, billing, support


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Rechaza el arranque en producción con configuración insegura."""
    problems = settings.security_problems()
    if settings.env == "prod" and problems:
        raise RuntimeError(
            "Configuración insegura para producción: " + "; ".join(problems)
        )
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Backend modular para la marca personal Renatx (renatx.com) — "
        "Franco Renato Palavecino | Cloud, Linux & IT Training (Hamburg, DE)."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.docs_enabled else None,
    redoc_url="/redoc" if settings.docs_enabled else None,
    openapi_url="/openapi.json" if settings.docs_enabled else None,
)

# CORS restringido a los orígenes configurados. En producción Traefik sirve
# web y API bajo el mismo origen, por lo que el navegador no necesita CORS.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/health", tags=["Infraestructura y Salud"])
def health_check() -> dict[str, Any]:
    """
    Endpoint de salud y diagnóstico del servicio.
    Usado por el frontend y por monitores de infraestructura.
    No expone detalles internos de la base de datos ni credenciales.
    """
    return {
        "status": "healthy",
        "brand": "Renatx (renatx.com)",
        "author": settings.owner,
        "environment": settings.env,
        "base_domain": settings.base_domain,
        "components": {"api": "ok"},
        "timestamp_utc": datetime.now(UTC).isoformat(),
    }


app.include_router(auth.router)
app.include_router(billing.router)
app.include_router(support.router)
