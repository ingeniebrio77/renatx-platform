"""
Tests para el módulo de seguridad (JWT creation, validation, get_current_user).
"""


import jwt
import pytest
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import create_access_token, get_current_user


class TestCreateAccessToken:
    """Tests para create_access_token."""

    def test_create_token_returns_string(self):
        """Debe devolver un string (token JWT)."""
        token = create_access_token(subject="test@renatx.com")
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_has_three_parts(self):
        """JWT debe tener 3 partes separadas por puntos."""
        token = create_access_token(subject="test@renatx.com")
        parts = token.split(".")
        assert len(parts) == 3

    def test_token_payload_contains_subject(self):
        """El payload debe contener el subject."""
        token = create_access_token(subject="renato@renatx.com")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["sub"] == "renato@renatx.com"

    def test_token_payload_contains_role(self):
        """El payload debe contener el role."""
        token = create_access_token(subject="test@test.com", role="admin")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["role"] == "admin"

    def test_token_payload_contains_brand(self):
        """El payload debe contener brand."""
        token = create_access_token(subject="test@test.com")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["brand"] == "renatx.com"

    def test_token_payload_contains_env(self):
        """El payload debe contener env."""
        token = create_access_token(subject="test@test.com")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["env"] == settings.env

    def test_token_payload_contains_iat_and_exp(self):
        """El payload debe contener iat (issued at) y exp (expiration)."""
        token = create_access_token(subject="test@test.com")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "iat" in payload
        assert "exp" in payload
        assert isinstance(payload["iat"], int)
        assert isinstance(payload["exp"], int)
        assert payload["exp"] > payload["iat"]

    def test_token_expiration_matches_config(self):
        """La expiración debe coincidir con JWT_EXPIRE_MINUTES."""
        token = create_access_token(subject="test@test.com")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        expected_exp = payload["iat"] + (settings.jwt_expire_minutes * 60)
        # Permitir diferencia de 1 segundo por tiempo de ejecución
        assert abs(payload["exp"] - expected_exp) <= 1

    def test_token_different_subjects_produce_different_tokens(self):
        """Subjects diferentes deben producir tokens diferentes."""
        token1 = create_access_token(subject="user1@test.com")
        token2 = create_access_token(subject="user2@test.com")
        assert token1 != token2

    def test_token_same_subject_produces_different_tokens(self):
        """Tokens con mismo subject deben ser diferentes (jti único)."""
        token1 = create_access_token(subject="test@test.com")
        token2 = create_access_token(subject="test@test.com")
        assert token1 != token2, "Tokens consecutivos deben ser diferentes"

        # Verificar que los payloads tienen jti diferentes (UUID único)
        import jwt
        payload1 = jwt.decode(
            token1, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        payload2 = jwt.decode(
            token2, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert "jti" in payload1
        assert "jti" in payload2
        assert payload1["jti"] != payload2["jti"], "jti debe ser único por token"

    def test_token_custom_role(self):
        """Debe aceptar role personalizado."""
        token = create_access_token(subject="test@test.com", role="premium")
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )
        assert payload["role"] == "premium"


class TestGetCurrentUser:
    """Tests para get_current_user (dependencia FastAPI)."""

    def test_valid_token_returns_user_dict(self, valid_jwt_token):
        """Token válido debe devolver dict con info del usuario."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=valid_jwt_token
        )
        user = get_current_user(credentials)
        assert isinstance(user, dict)
        assert user["username"] == "renato@renatx.com"
        assert user["role"] == "sysadmin"
        assert "env" in user
        assert "expires_at" in user

    def test_none_credentials_raises_401(self):
        """Credenciales None debe lanzar HTTPException 401."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(None)
        assert exc_info.value.status_code == 401
        assert "Falta cabecera" in exc_info.value.detail

    def test_invalid_token_raises_401(self, invalid_jwt_token):
        """Token con firma inválida debe lanzar 401."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=invalid_jwt_token
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert "inválido" in exc_info.value.detail.lower()

    def test_expired_token_raises_401(self, expired_jwt_token):
        """Token expirado debe lanzar 401."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials=expired_jwt_token
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401
        assert "expirado" in exc_info.value.detail.lower()

    def test_malformed_token_raises_401(self):
        """Token malformado debe lanzar 401."""
        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="no-es-un-jwt-valido"
        )
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_token_with_missing_sub_returns_none_username(self):
        """Token sin 'sub' debe devolver username=None."""
        import jwt
        from fastapi.security import HTTPAuthorizationCredentials

        payload = {"role": "user", "brand": "renatx.com", "env": "test"}
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = get_current_user(credentials)
        assert user["username"] is None

    def test_token_with_missing_role_defaults_to_user(self):
        """Token sin 'role' debe devolver role='user'."""
        import jwt
        from fastapi.security import HTTPAuthorizationCredentials

        payload = {"sub": "test@test.com", "brand": "renatx.com", "env": "test"}
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
        user = get_current_user(credentials)
        assert user["role"] == "user"


class TestSecurityEdgeCases:
    """Tests de casos borde de seguridad."""

    def test_algorithm_confusion_attack_prevented(self):
        """Debe rechazar tokens con algoritmo 'none' o diferente."""
        import jwt

        # Token con algoritmo 'none' (ataque de confusión de algoritmo)
        payload = {"sub": "attacker@test.com", "role": "admin"}
        token_none = jwt.encode(payload, "", algorithm="none")

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_none)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_token_with_different_algorithm_rejected(self):
        """Token firmado con RS256 debe ser rechazado (esperamos HS256)."""
        import jwt
        from cryptography.hazmat.primitives.asymmetric import rsa

        private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        payload = {"sub": "attacker@test.com", "role": "admin"}
        token_rs256 = jwt.encode(payload, private_key, algorithm="RS256")

        from fastapi.security import HTTPAuthorizationCredentials

        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token_rs256)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_very_long_token_rejected(self):
        """Token extremadamente largo debe ser rechazado."""
        from fastapi.security import HTTPAuthorizationCredentials

        long_token = "x" * 10000
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=long_token)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_token_tampering_detected(self, valid_jwt_token):
        """Modificación de cualquier carácter del token debe ser detectada."""
        from fastapi.security import HTTPAuthorizationCredentials

        # Cambiar último carácter
        tampered = valid_jwt_token[:-1] + ("x" if valid_jwt_token[-1] != "x" else "y")
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials=tampered)
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(credentials)
        assert exc_info.value.status_code == 401

    def test_secret_key_not_in_token(self, valid_jwt_token):
        """La clave secreta NO debe aparecer en el token."""
        assert settings.jwt_secret_key not in valid_jwt_token
        # El token no debe contener partes de la clave
        for part in valid_jwt_token.split("."):
            assert len(part) < len(settings.jwt_secret_key) or settings.jwt_secret_key not in part