"""
Tests para los endpoints de autenticación JWT (/auth/login, /auth/me).
"""

from fastapi.testclient import TestClient


class TestAuthLogin:
    """Tests para POST /auth/login."""

    def test_login_with_valid_credentials_returns_token(
        self, test_client: TestClient
    ):
        """Credenciales válidas deben devolver token JWT."""
        response = test_client.post(
            "/auth/login",
            json={"username": "renato@renatx.com", "password": "linux-admin-demo"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in_minutes" in data
        assert data["environment"] == "test"

    def test_login_token_is_valid_jwt(self, test_client: TestClient):
        """El token devuelto debe ser un JWT válido decodificable."""
        import jwt

        response = test_client.post(
            "/auth/login",
            json={"username": "renato@renatx.com", "password": "linux-admin-demo"},
        )
        token = response.json()["access_token"]

        # Debe poder decodificarse con la clave secreta de test
        payload = jwt.decode(
            token, "test_secret_key_for_testing_only_32chars", algorithms=["HS256"]
        )
        assert payload["sub"] == "renato@renatx.com"
        assert payload["role"] == "sysadmin"
        assert payload["brand"] == "renatx.com"
        assert "exp" in payload
        assert "iat" in payload

    def test_login_with_empty_username_fails(self, test_client: TestClient):
        """Username vacío debe fallar con 401."""
        response = test_client.post(
            "/auth/login",
            json={"username": "", "password": "linux-admin-demo"},
        )
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]

    def test_login_with_short_password_fails(self, test_client: TestClient):
        """Contraseña muy corta debe fallar con 401."""
        response = test_client.post(
            "/auth/login",
            json={"username": "renato@renatx.com", "password": "123"},
        )
        assert response.status_code == 401
        assert "Credenciales inválidas" in response.json()["detail"]

    def test_login_accepts_any_username_with_valid_password(self, test_client: TestClient):
        """El endpoint acepta cualquier username si la password tiene >= 4 chars (sin BD de usuarios)."""
        response = test_client.post(
            "/auth/login",
            json={"username": "cualquiera@dominio.com", "password": "linux-admin-demo"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    def test_login_accepts_any_password_with_min_length(self, test_client: TestClient):
        """El endpoint acepta cualquier password con longitud >= 4."""
        response = test_client.post(
            "/auth/login",
            json={"username": "renato@renatx.com", "password": "pass123"},
        )
        assert response.status_code == 200

    def test_login_with_missing_fields_uses_defaults(self, test_client: TestClient):
        """Campos faltantes usan valores por defecto del schema (username/password por defecto)."""
        response = test_client.post("/auth/login", json={})
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        # Token debe ser decodificable con defaults
        import jwt
        payload = jwt.decode(
            data["access_token"],
            "test_secret_key_for_testing_only_32chars",
            algorithms=["HS256"],
        )
        assert payload["sub"] == "renato@renatx.com"

    def test_login_response_schema_matches_token_response(self, test_client: TestClient):
        """La respuesta debe coincidir con el esquema TokenResponse."""
        from app.schemas import TokenResponse

        response = test_client.post(
            "/auth/login",
            json={"username": "renato@renatx.com", "password": "linux-admin-demo"},
        )
        # Validar con Pydantic
        TokenResponse(**response.json())


class TestAuthMe:
    """Tests para GET /auth/me (protegido con JWT)."""

    def test_me_with_valid_token_returns_user_info(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Token válido debe devolver info del usuario autenticado."""
        response = test_client.get("/auth/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["authenticated"] is True
        assert "user" in data
        assert data["user"]["username"] == "renato@renatx.com"
        assert data["user"]["role"] == "sysadmin"
        assert data["platform"] == "Renatx (renatx.com)"

    def test_me_without_token_returns_401(self, test_client: TestClient):
        """Sin token debe fallar con 401."""
        response = test_client.get("/auth/me")
        assert response.status_code == 401
        assert "Falta cabecera" in response.json()["detail"]

    def test_me_with_invalid_token_returns_401(
        self, test_client: TestClient, invalid_jwt_token: str
    ):
        """Token con firma inválida debe fallar con 401."""
        response = test_client.get(
            "/auth/me", headers={"Authorization": f"Bearer {invalid_jwt_token}"}
        )
        assert response.status_code == 401
        assert "inválido" in response.json()["detail"].lower()

    def test_me_with_expired_token_returns_401(
        self, test_client: TestClient, expired_jwt_token: str
    ):
        """Token expirado debe fallar con 401."""
        response = test_client.get(
            "/auth/me", headers={"Authorization": f"Bearer {expired_jwt_token}"}
        )
        assert response.status_code == 401
        assert "expirado" in response.json()["detail"].lower()

    def test_me_with_malformed_bearer_header_returns_401(self, test_client: TestClient):
        """Header Authorization malformado debe fallar."""
        response = test_client.get("/auth/me", headers={"Authorization": "Bearer"})
        assert response.status_code == 401

    def test_me_with_bearer_token_extra_spaces_works(
        self, test_client: TestClient, valid_jwt_token: str
    ):
        """Header con espacios extra alrededor del token debe funcionar."""
        response = test_client.get(
            "/auth/me", headers={"Authorization": f"Bearer  {valid_jwt_token}  "}
        )
        assert response.status_code == 200

    def test_me_token_payload_contains_required_fields(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """El payload del token debe contener campos requeridos."""
        response = test_client.get("/auth/me", headers=auth_headers)
        user = response.json()["user"]
        required = ["username", "role", "env", "expires_at"]
        for field in required:
            assert field in user, f"Falta {field} en user payload"