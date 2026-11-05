"""
Tests para el endpoint de salud (/health).
Verifica que la API responde correctamente y expone la información esperada.
"""

from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests para GET /health."""

    def test_health_returns_200(self, test_client: TestClient):
        """El endpoint de salud debe responder con HTTP 200."""
        response = test_client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json(self, test_client: TestClient):
        """La respuesta debe ser JSON válido."""
        response = test_client.get("/health")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)

    def test_health_contains_required_fields(self, test_client: TestClient):
        """La respuesta debe contener todos los campos obligatorios."""
        response = test_client.get("/health")
        data = response.json()

        required_fields = [
            "status",
            "brand",
            "author",
            "environment",
            "base_domain",
            "components",
            "timestamp_utc",
        ]
        for field in required_fields:
            assert field in data, f"Falta campo requerido: {field}"

    def test_health_does_not_leak_database_details(self, test_client: TestClient):
        """El endpoint público no debe exponer host, puerto ni nombre de la BD."""
        data = test_client.get("/health").json()
        assert "database_target" not in data
        serialized = str(data)
        assert "test_db" not in serialized
        assert "5432" not in serialized
        assert data["components"] == {"api": "ok"}

    def test_health_status_is_healthy(self, test_client: TestClient):
        """El campo status debe ser 'healthy'."""
        response = test_client.get("/health")
        assert response.json()["status"] == "healthy"

    def test_health_brand_is_renatx(self, test_client: TestClient):
        """El campo brand debe contener 'Renatx'."""
        response = test_client.get("/health")
        assert "Renatx" in response.json()["brand"]

    def test_health_environment_is_test(self, test_client: TestClient):
        """En entorno de test, environment debe ser 'test'."""
        response = test_client.get("/health")
        assert response.json()["environment"] == "test"

    def test_health_base_domain_is_localhost(self, test_client: TestClient):
        """En local, base_domain debe ser renatx.localhost."""
        response = test_client.get("/health")
        assert response.json()["base_domain"] == "renatx.localhost"

    def test_health_database_details_not_present(self, test_client: TestClient):
        """database_target ya no forma parte de la respuesta pública."""
        response = test_client.get("/health")
        assert "database_target" not in response.json()

    def test_health_timestamp_is_valid_iso(self, test_client: TestClient):
        """timestamp_utc debe ser una fecha ISO 8601 válida."""
        from datetime import datetime

        response = test_client.get("/health")
        timestamp = response.json()["timestamp_utc"]
        # Debe poder parsearse sin error
        parsed = datetime.fromisoformat(timestamp)
        assert parsed is not None

    def test_health_response_time_under_100ms(self, test_client: TestClient):
        """El endpoint debe responder en menos de 100ms (rendimiento básico)."""
        import time

        start = time.perf_counter()
        response = test_client.get("/health")
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert response.status_code == 200
        assert elapsed_ms < 100, f"Endpoint demasiado lento: {elapsed_ms:.1f}ms"