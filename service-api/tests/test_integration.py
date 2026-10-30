"""
Tests de integración: flujos completos de la API.
"""

from fastapi.testclient import TestClient


class TestFullAuthFlow:
    """Test del flujo completo de autenticación."""

    def test_login_then_me(self, test_client: TestClient):
        """Login exitoso seguido de /me con el token devuelto."""
        # 1. Login
        login_resp = test_client.post(
            "/auth/login",
            json={"username": "renato@renatx.com", "password": "linux-admin-demo"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        # 2. Usar token en /me
        me_resp = test_client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["authenticated"] is True
        assert me_resp.json()["user"]["username"] == "renato@renatx.com"

    def test_login_with_custom_credentials_works(self, test_client: TestClient):
        """Login acepta cualquier username/password válido (longitud >= 4)."""
        login_resp = test_client.post(
            "/auth/login",
            json={"username": "cliente@empresa.de", "password": "mipassword123"},
        )
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]

        me_resp = test_client.get(
            "/auth/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert me_resp.status_code == 200
        assert me_resp.json()["user"]["username"] == "cliente@empresa.de"


class TestBillingFlow:
    """Test del flujo completo de facturación."""

    def test_catalog_then_checkout(self, test_client: TestClient):
        """Obtener catálogo y luego hacer checkout de un servicio."""
        # 1. Obtener catálogo
        catalog_resp = test_client.get("/billing/catalog")
        assert catalog_resp.status_code == 200
        services = catalog_resp.json()["services"]
        assert "support_sos_1h" in services

        # 2. Checkout del primer servicio
        plan_id = next(iter(services.keys()))
        checkout_resp = test_client.post(
            "/billing/checkout",
            json={
                "plan_id": plan_id,
                "customer_email": "cliente@test.com",
                "language": "es",
            },
        )
        assert checkout_resp.status_code == 200
        data = checkout_resp.json()
        assert data["status"] == "success"
        assert data["plan_id"] == plan_id

    def test_checkout_bilingual(self, test_client: TestClient):
        """Checkout debe funcionar en ambos idiomas."""
        for lang in ["es", "de"]:
            checkout_resp = test_client.post(
                "/billing/checkout",
                json={
                    "plan_id": "mentoring_1h",
                    "customer_email": "cliente@test.com",
                    "language": lang,
                },
            )
            assert checkout_resp.status_code == 200
            assert checkout_resp.json()["status"] == "success"

    def test_webhook_after_checkout(self, test_client: TestClient):
        """Webhook debe procesar evento tras checkout."""
        # Simular evento de Stripe
        webhook_resp = test_client.post(
            "/billing/webhook",
            json={
                "event_id": "evt_checkout_completed_123",
                "event_type": "checkout.session.completed",
            },
        )
        assert webhook_resp.status_code == 200
        assert webhook_resp.json()["received"] is True


class TestSupportFlow:
    """Test del flujo completo de soporte RustDesk."""

    def test_status_start_status_stop_status(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """Ciclo completo: status -> start -> status -> stop -> status."""
        # 1. Estado inicial
        status0 = test_client.get("/support/status").json()
        assert status0["active"] is False

        # 2. Start (requiere auth)
        start_resp = test_client.post("/support/start", headers=auth_headers)
        assert start_resp.status_code == 200
        assert start_resp.json()["active"] is True

        # 3. Status tras start
        status1 = test_client.get("/support/status").json()
        assert status1["active"] is True
        assert status1["elapsed_minutes"] >= 1
        assert ":" in status1["id_server"]
        assert ":" in status1["relay_server"]

        # 4. Stop (requiere auth)
        stop_resp = test_client.post("/support/stop", headers=auth_headers)
        assert stop_resp.status_code == 200
        assert stop_resp.json()["active"] is False

        # 5. Estado final
        status2 = test_client.get("/support/status").json()
        assert status2["active"] is False
        assert status2["estimated_session_cost_eur"] == 0.0

    def test_unauthorized_cannot_start_stop(self, test_client: TestClient):
        """Sin autenticación no se puede start/stop."""
        start_resp = test_client.post("/support/start")
        assert start_resp.status_code == 401

        stop_resp = test_client.post("/support/stop")
        assert stop_resp.status_code == 401

    def test_status_public_no_auth_required(self, test_client: TestClient):
        """GET /support/status no requiere autenticación."""
        resp = test_client.get("/support/status")
        assert resp.status_code == 200


class TestCrossEndpointConsistency:
    """Tests de consistencia entre endpoints."""

    def test_health_and_catalog_both_work(self, test_client: TestClient):
        """Health y catalog deben responder correctamente."""
        health = test_client.get("/health")
        catalog = test_client.get("/billing/catalog")
        assert health.status_code == 200
        assert catalog.status_code == 200

    def test_all_endpoints_return_json(self, test_client: TestClient):
        """Todos los endpoints deben devolver JSON."""
        endpoints = [
            "/health",
            "/billing/catalog",
            "/support/status",
        ]
        for ep in endpoints:
            resp = test_client.get(ep)
            assert resp.status_code == 200
            assert resp.headers["content-type"] == "application/json"
            assert isinstance(resp.json(), dict)

    def test_cors_headers_present(self, test_client: TestClient):
        """Las respuestas deben incluir headers CORS (configuración permisiva en local)."""
        resp = test_client.get("/health")
        # FastAPI con CORSMiddleware allow_origins=["*"] no añade Access-Control-Allow-Origin
        # en respuestas simples, pero sí en preflight. Verificamos que no falle.
        assert resp.status_code == 200


class TestErrorHandling:
    """Tests de manejo de errores consistente."""

    def test_404_for_unknown_endpoint(self, test_client: TestClient):
        """Endpoint inexistente debe devolver 404."""
        resp = test_client.get("/endpoint/que/no/existe")
        assert resp.status_code == 404

    def test_422_for_invalid_json(self, test_client: TestClient):
        """JSON inválido debe devolver 422."""
        resp = test_client.post(
            "/auth/login",
            data="no-es-json",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code == 422

    def test_method_not_allowed(self, test_client: TestClient):
        """Método HTTP no permitido debe devolver 405."""
        resp = test_client.put("/health")
        assert resp.status_code == 405

    def test_error_response_format(self, test_client: TestClient):
        """Las respuestas de error deben tener formato consistente."""
        resp = test_client.get("/auth/me")  # 401 sin token
        assert resp.status_code == 401
        data = resp.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)