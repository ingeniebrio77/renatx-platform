"""
Tests para los endpoints de soporte remoto RustDesk (/support/status, /support/start, /support/stop).
"""

import time
from datetime import datetime

from fastapi.testclient import TestClient


class TestSupportStatus:
    """Tests para GET /support/status (público)."""

    def test_status_returns_200(self, test_client: TestClient):
        response = test_client.get("/support/status")
        assert response.status_code == 200

    def test_status_returns_complete_structure(self, test_client: TestClient):
        """La respuesta debe contener todos los campos del esquema RustDeskStatusResponse."""
        from app.schemas import RustDeskStatusResponse

        response = test_client.get("/support/status")
        RustDeskStatusResponse(**response.json())

    def test_status_default_is_standby(self, test_client: TestClient):
        """Por defecto el servidor debe estar en STANDBY (apagado)."""
        response = test_client.get("/support/status")
        data = response.json()
        assert data["active"] is False
        assert "STANDBY" in data["status_label"]
        assert data["elapsed_minutes"] == 0
        assert data["estimated_session_cost_eur"] == 0.0
        assert data["started_at_utc"] is None

    def test_status_standby_shows_placeholder_values(self, test_client: TestClient):
        """En STANDBY debe mostrar placeholders en lugar de credenciales reales."""
        response = test_client.get("/support/status")
        data = response.json()
        assert "Espera" in data["id_server"] or "—" in data["id_server"]
        assert "Espera" in data["relay_server"] or "—" in data["relay_server"]
        assert "habilita al activar" in data["public_key"] or "—" in data["public_key"]

    def test_status_includes_bilingual_instructions(self, test_client: TestClient):
        """Debe incluir instrucciones en español y alemán."""
        response = test_client.get("/support/status")
        data = response.json()
        assert "instructions_es" in data
        assert "instructions_de" in data
        assert len(data["instructions_es"]) > 0
        assert len(data["instructions_de"]) > 0

    def test_status_hourly_rate_is_correct(self, test_client: TestClient):
        """La tarifa por hora debe ser 0.007 EUR."""
        response = test_client.get("/support/status")
        assert response.json()["hourly_rate_eur"] == 0.007

    def test_status_public_key_format(self, test_client: TestClient):
        """La clave pública debe tener formato base64-like."""
        response = test_client.get("/support/status")
        # En standby muestra placeholder, al activar muestra clave real
        key = response.json()["public_key"]
        assert isinstance(key, str)
        assert len(key) > 0


class TestSupportStartStop:
    """Tests para POST /support/start y POST /support/stop (protegidos con JWT)."""

    def test_start_requires_authentication(self, test_client: TestClient):
        """Encender nodo requiere JWT válido."""
        response = test_client.post("/support/start")
        assert response.status_code == 401

    def test_start_with_valid_token_activates_server(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Token válido debe activar el servidor RustDesk."""
        response = test_client.post("/support/start", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is True
        assert "ONLINE" in data["status_label"]
        assert data["elapsed_minutes"] >= 1
        assert data["estimated_session_cost_eur"] >= 0
        assert data["started_at_utc"] is not None
        assert data["id_server"] != "—"
        assert data["relay_server"] != "—"
        assert data["public_key"] != "—"

    def test_start_returns_valid_connection_data(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Al activar debe devolver datos de conexión válidos para el cliente."""
        response = test_client.post("/support/start", headers=auth_headers)
        data = response.json()
        assert ":" in data["id_server"]  # host:puerto
        assert ":" in data["relay_server"]
        # Clave pública base64
        assert len(data["public_key"]) > 20

    def test_start_idempotent_multiple_calls(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Llamadas múltiples a start deben ser idempotentes (no crear múltiples instancias)."""
        test_client.post("/support/start", headers=auth_headers)
        response1 = test_client.post("/support/start", headers=auth_headers)
        response2 = test_client.post("/support/start", headers=auth_headers)

        # Ambas deben devolver 200 y estado activo
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["active"] is True
        assert response2.json()["active"] is True
        # started_at_utc debe ser muy cercano (misma instancia, diferencia < 1 segundo)
        t1 = datetime.fromisoformat(response1.json()["started_at_utc"])
        t2 = datetime.fromisoformat(response2.json()["started_at_utc"])
        diff_seconds = abs((t1 - t2).total_seconds())
        assert diff_seconds < 1.0, f"Timestamps difieren en {diff_seconds}s (deberían ser casi idénticos)"

    def test_stop_requires_authentication(self, test_client: TestClient):
        """Apagar nodo requiere JWT válido."""
        response = test_client.post("/support/stop")
        assert response.status_code == 401

    def test_stop_deactivates_server(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Token válido debe desactivar el servidor."""
        # Primero activar
        test_client.post("/support/start", headers=auth_headers)
        # Luego desactivar
        response = test_client.post("/support/stop", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["active"] is False
        assert "STANDBY" in data["status_label"]
        assert data["elapsed_minutes"] == 0
        assert data["estimated_session_cost_eur"] == 0.0
        assert data["started_at_utc"] is None

    def test_stop_returns_placeholder_values(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Al apagar debe volver a mostrar placeholders."""
        test_client.post("/support/start", headers=auth_headers)
        response = test_client.post("/support/stop", headers=auth_headers)
        data = response.json()
        assert "Espera" in data["id_server"] or "—" in data["id_server"]
        assert "Espera" in data["relay_server"] or "—" in data["relay_server"]
        assert "habilita al activar" in data["public_key"] or "—" in data["public_key"]

    def test_stop_idempotent_multiple_calls(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Llamadas múltiples a stop deben ser idempotentes."""
        test_client.post("/support/start", headers=auth_headers)
        test_client.post("/support/stop", headers=auth_headers)
        response1 = test_client.post("/support/stop", headers=auth_headers)
        response2 = test_client.post("/support/stop", headers=auth_headers)

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response1.json()["active"] is False
        assert response2.json()["active"] is False

    def test_full_cycle_start_status_stop(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Ciclo completo: status -> start -> status -> stop -> status."""
        # 1. Estado inicial: STANDBY
        status0 = test_client.get("/support/status").json()
        assert status0["active"] is False

        # 2. Start
        start_resp = test_client.post("/support/start", headers=auth_headers)
        assert start_resp.status_code == 200
        assert start_resp.json()["active"] is True

        # 3. Status tras start: ACTIVO
        status1 = test_client.get("/support/status").json()
        assert status1["active"] is True
        assert status1["elapsed_minutes"] >= 1

        # 4. Stop
        stop_resp = test_client.post("/support/stop", headers=auth_headers)
        assert stop_resp.status_code == 200
        assert stop_resp.json()["active"] is False

        # 5. Estado final: STANDBY
        status2 = test_client.get("/support/status").json()
        assert status2["active"] is False
        assert status2["estimated_session_cost_eur"] == 0.0

    def test_cost_calculation_increases_with_time(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """El coste estimado debe aumentar con el tiempo transcurrido."""
        test_client.post("/support/start", headers=auth_headers)
        status1 = test_client.get("/support/status").json()
        cost1 = status1["estimated_session_cost_eur"]

        # Pequeña pausa
        time.sleep(0.1)

        status2 = test_client.get("/support/status").json()
        cost2 = status2["estimated_session_cost_eur"]

        # El coste no debe disminuir (redondeo a 5 decimales puede mantenerlo igual en poco tiempo)
        assert cost2 >= cost1


class TestSupportAuthEdgeCases:
    """Tests de casos borde de autenticación en /support."""

    def test_start_with_expired_token_fails(
        self, test_client: TestClient, expired_jwt_token: str
    ):
        response = test_client.post(
            "/support/start", headers={"Authorization": f"Bearer {expired_jwt_token}"}
        )
        assert response.status_code == 401

    def test_start_with_invalid_token_fails(
        self, test_client: TestClient, invalid_jwt_token: str
    ):
        response = test_client.post(
            "/support/start", headers={"Authorization": f"Bearer {invalid_jwt_token}"}
        )
        assert response.status_code == 401

    def test_stop_with_expired_token_fails(
        self, test_client: TestClient, auth_headers: dict[str, str], expired_jwt_token: str
    ):
        test_client.post("/support/start", headers=auth_headers)
        response = test_client.post(
            "/support/stop", headers={"Authorization": f"Bearer {expired_jwt_token}"}
        )
        assert response.status_code == 401


class TestSupportSchemaValidation:
    """Tests de validación de esquemas Pydantic."""

    def test_status_response_matches_schema(self, test_client: TestClient):
        from app.schemas import RustDeskStatusResponse

        response = test_client.get("/support/status")
        RustDeskStatusResponse(**response.json())

    def test_start_response_matches_schema(self, test_client: TestClient, auth_headers: dict[str, str]):
        from app.schemas import RustDeskStatusResponse

        response = test_client.post("/support/start", headers=auth_headers)
        RustDeskStatusResponse(**response.json())

    def test_stop_response_matches_schema(self, test_client: TestClient, auth_headers: dict[str, str]):
        from app.schemas import RustDeskStatusResponse

        test_client.post("/support/start", headers=auth_headers)
        response = test_client.post("/support/stop", headers=auth_headers)
        RustDeskStatusResponse(**response.json())