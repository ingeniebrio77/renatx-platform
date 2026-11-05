"""Endpoints de autenticación JWT (`/auth/login` y `/auth/me`)."""

import secrets
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.config import settings
from app.core.passwords import verify_password
from app.core.ratelimit import SlidingWindowRateLimiter
from app.core.security import create_access_token, get_current_user
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación JWT"])

# Límite de intentos por IP (en memoria, suficiente para un único proceso).
login_limiter = SlidingWindowRateLimiter(
    max_attempts=settings.login_rate_limit_attempts,
    window_seconds=settings.login_rate_limit_window_seconds,
)


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(payload: LoginRequest, request: Request) -> TokenResponse:
    """
    Verifica el usuario y el hash PBKDF2 del administrador y emite un JWT.

    - 429 si se superan los intentos permitidos por IP.
    - 503 si el servidor no tiene `ADMIN_PASSWORD_HASH` configurado.
    - 401 para cualquier credencial incorrecta (mismo mensaje siempre).
    """
    client_ip = request.client.host if request.client else "desconocida"
    if not login_limiter.allow(client_ip):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Demasiados intentos de inicio de sesión. Inténtalo más tarde.",
            headers={"Retry-After": str(login_limiter.window_seconds)},
        )

    if not settings.admin_password_hash:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Autenticación no configurada en el servidor. "
                "Define ADMIN_PASSWORD_HASH (make password-hash)."
            ),
        )

    # Se evalúan ambos factores siempre para no filtrar cuál falló.
    username_ok = secrets.compare_digest(payload.username, settings.admin_username)
    password_ok = verify_password(payload.password, settings.admin_password_hash)

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
        )

    token = create_access_token(subject=payload.username, role="sysadmin")
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.jwt_expire_minutes,
        environment=settings.env,
    )


@router.get("/me")
def read_current_user(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)]
) -> dict[str, Any]:
    """
    Ruta protegida: requiere enviar `Authorization: Bearer <token>`.
    Devuelve los datos decodificados del token JWT.
    """
    return {
        "authenticated": True,
        "user": current_user,
        "platform": "Renatx (renatx.com)",
        "owner": settings.owner,
    }
