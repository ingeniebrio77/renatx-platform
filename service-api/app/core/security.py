"""
Seguridad y Autenticación JWT — Explicación Pedagógica para Administradores de Sistemas:

Un JSON Web Token (JWT) funciona de forma similar a un ticket firmado criptográficamente
(como un certificado SSH o un ticket Kerberos ligero):
1. El cliente envía credenciales en `POST /auth/login`.
2. El servidor devuelve un token firmado con `JWT_SECRET_KEY` (algoritmo HMAC-SHA256).
3. En las siguientes peticiones HTTP, el cliente envía la cabecera:
   `Authorization: Bearer <token>`
4. La dependencia `get_current_user` verifica la firma y la fecha de expiración (`exp`)
   sin necesidad de guardar sesiones en memoria del servidor (stateless).
"""

from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import settings

# Esquema estándar HTTP Bearer para extraer el token de la cabecera Authorization
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(subject: str, role: str = "admin") -> str:
    """Genera un token JWT firmado con tiempo de expiración."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.jwt_expire_minutes)

    payload: dict[str, Any] = {
        "sub": subject,
        "role": role,
        "brand": "renatx.com",
        "env": settings.env,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    """
    Dependencia reutilizable de FastAPI.
    Verifica que la petición incluya un token JWT válido antes de ejecutar la ruta.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta cabecera 'Authorization: Bearer <token>'",
        )

    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        return {
            "username": payload.get("sub"),
            "role": payload.get("role", "user"),
            "env": payload.get("env"),
            "expires_at": payload.get("exp"),
        }
    except jwt.ExpiredSignatureError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token JWT ha expirado",
        ) from exc
    except jwt.InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT inválido o firma incorrecta",
        ) from exc
