"""
Configuración compartida de pytest para service-api.
Proporciona fixtures comunes para tests unitarios y de integración.
"""

import os
from collections.abc import Generator
from datetime import UTC, datetime

import pytest
from fastapi.testclient import TestClient

# Configurar variables de entorno ANTES de importar la app
os.environ.setdefault("ENV", "test")
os.environ.setdefault("BASE_DOMAIN", "renatx.localhost")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_password")
os.environ.setdefault("POSTGRES_DB", "test_db")
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("JWT_SECRET_KEY", "test_secret_key_for_testing_only_32chars")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRE_MINUTES", "60")
os.environ.setdefault("STRIPE_SECRET_KEY", "sk_test_mock_renatx_000000000000")
os.environ.setdefault("STRIPE_WEBHOOK_SECRET", "whsec_mock_renatx_000000000000")
os.environ.setdefault("STRIPE_PRICE_ID_PRO", "price_mock_renatx_pro_monthly")
os.environ.setdefault("ADMIN_USERNAME", "renato@renatx.com")

# Hash real generado en tiempo de test (iteraciones bajas para que sea rápido).
from app.core.passwords import hash_password

TEST_ADMIN_PASSWORD = "linux-admin-demo"
os.environ.setdefault("ADMIN_PASSWORD_HASH", hash_password(TEST_ADMIN_PASSWORD, iterations=1000))

from app.core.security import create_access_token
from app.main import app
from app.routers.auth import login_limiter


@pytest.fixture(autouse=True)
def _reset_login_limiter() -> Generator[None, None, None]:
    """Evita que el rate limit de login contamine tests consecutivos."""
    login_limiter.reset()
    yield
    login_limiter.reset()


@pytest.fixture(scope="session")
def test_client() -> Generator[TestClient, None, None]:
    """Cliente de prueba síncrono para tests rápidos."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def valid_jwt_token() -> str:
    """Genera un token JWT válido para tests de autenticación."""
    return create_access_token(subject="renato@renatx.com", role="sysadmin")


@pytest.fixture
def expired_jwt_token() -> str:
    """Genera un token JWT expirado (para test de expiración)."""
    from datetime import timedelta

    import jwt

    from app.core.config import settings

    past = datetime.now(UTC) - timedelta(minutes=10)
    payload = {
        "sub": "renato@renatx.com",
        "role": "sysadmin",
        "brand": "renatx.com",
        "env": "test",
        "iat": int(past.timestamp()),
        "exp": int((past + timedelta(minutes=1)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


@pytest.fixture
def invalid_jwt_token() -> str:
    """Token JWT con firma incorrecta."""
    import jwt

    payload = {"sub": "renato@renatx.com", "role": "sysadmin"}
    return jwt.encode(payload, "wrong_secret_key", algorithm="HS256")


@pytest.fixture
def auth_headers(valid_jwt_token: str) -> dict[str, str]:
    """Headers de autorización con token válido."""
    return {"Authorization": f"Bearer {valid_jwt_token}"}


@pytest.fixture
def stripe_signature():
    """Genera cabeceras `Stripe-Signature` válidas para un cuerpo dado."""
    import hashlib
    import hmac
    import time

    from app.core.config import settings

    def _sign(body: bytes, timestamp: int | None = None) -> str:
        ts = int(time.time()) if timestamp is None else timestamp
        signed = f"{ts}.".encode("ascii") + body
        digest = hmac.new(
            settings.stripe_webhook_secret.encode("utf-8"), signed, hashlib.sha256
        ).hexdigest()
        return f"t={ts},v1={digest}"

    return _sign


@pytest.fixture
def sample_catalog() -> dict:
    """Catálogo de servicios de referencia para tests."""
    return {
        "support_sos_1h": {
            "title_es": "Soporte Remoto S.O.S. Linux / Cloud / Redes (1 Hora via RustDesk)",
            "title_de": "Linux / Cloud / Netzwerk Remote-Support S.O.S. (1 Stunde via RustDesk)",
            "amount_eur": 65.00,
            "mode": "payment",
        },
        "mentoring_1h": {
            "title_es": "Mentoría Técnica 1-a-1: Fachinformatiker (FISI) / Network+ / AWS (60 min)",
            "title_de": "1:1 IT-Mentoring & Prüfungsvorbereitung: FISI / Network+ / AWS (60 Min.)",
            "amount_eur": 49.00,
            "mode": "payment",
        },
        "devops_pack_5h": {
            "title_es": "Bono 5 Sesiones Prácticas: De Cero a DevOps (Terraform, Ansible, Podman)",
            "title_de": "5er-Paket Hands-On: IaC & DevOps (Terraform, Ansible, Podman & Traefik)",
            "amount_eur": 220.00,
            "mode": "payment",
        },
    }
