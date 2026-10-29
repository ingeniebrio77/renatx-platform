"""Endpoints de autenticación JWT (`/auth/login` y `/auth/me`)."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.schemas import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["Autenticación JWT"])


@router.post("/login", response_model=TokenResponse)
def login_for_access_token(payload: LoginRequest) -> TokenResponse:
    """
    Endpoint pedagógico de inicio de sesión.
    Verifica credenciales de prueba y emite un token JWT firmado.
    """
    if not payload.username or len(payload.password) < 4:
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
def read_current_user(current_user: dict[str, Any] = Depends(get_current_user)) -> dict[str, Any]:
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
