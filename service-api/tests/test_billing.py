"""
Tests para los endpoints de facturación y catálogo (/billing/catalog, /billing/checkout, /billing/webhook).
"""

import pytest
from fastapi.testclient import TestClient


class TestBillingCatalog:
    """Tests para GET /billing/catalog."""

    def test_catalog_returns_200(self, test_client: TestClient):
        response = test_client.get("/billing/catalog")
        assert response.status_code == 200

    def test_catalog_returns_currency_eur(self, test_client: TestClient):
        response = test_client.get("/billing/catalog")
        assert response.json()["currency"] == "EUR"

    def test_catalog_contains_all_three_services(self, test_client: TestClient):
        response = test_client.get("/billing/catalog")
        services = response.json()["services"]
        expected_ids = {"support_sos_1h", "mentoring_1h", "devops_pack_5h"}
        assert set(services.keys()) == expected_ids

    def test_catalog_service_structure(self, test_client: TestClient):
        """Cada servicio debe tener la estructura completa."""
        response = test_client.get("/billing/catalog")
        for service in response.json()["services"].values():
            required_fields = [
                "title_es",
                "title_de",
                "amount_eur",
                "mode",
            ]
            for field in required_fields:
                assert field in service, f"Falta {field} en servicio"

    def test_catalog_prices_are_positive(self, test_client: TestClient):
        """Todos los precios deben ser positivos."""
        response = test_client.get("/billing/catalog")
        for service in response.json()["services"].values():
            assert service["amount_eur"] > 0

    def test_catalog_prices_match_expected(self, test_client: TestClient):
        """Los precios deben coincidir con los valores de negocio."""
        response = test_client.get("/billing/catalog")
        services = response.json()["services"]
        assert services["support_sos_1h"]["amount_eur"] == 65.00
        assert services["mentoring_1h"]["amount_eur"] == 49.00
        assert services["devops_pack_5h"]["amount_eur"] == 220.00

    def test_catalog_mode_is_payment(self, test_client: TestClient):
        """Todos los servicios deben ser modo 'payment' (pago único)."""
        response = test_client.get("/billing/catalog")
        for service in response.json()["services"].values():
            assert service["mode"] == "payment"


class TestBillingCheckout:
    """Tests para POST /billing/checkout."""

    @pytest.mark.parametrize(
        "plan_id,expected_amount",
        [
            ("support_sos_1h", 65.00),
            ("mentoring_1h", 49.00),
            ("devops_pack_5h", 220.00),
        ],
    )
    def test_checkout_returns_success_for_valid_plan(
        self, test_client: TestClient, plan_id: str, expected_amount: float
    ):
        """Checkout debe funcionar para cada plan válido."""
        response = test_client.post(
            "/billing/checkout",
            json={
                "plan_id": plan_id,
                "customer_email": "cliente@empresa.de",
                "language": "es",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["plan_id"] == plan_id
        assert data["amount_eur"] == expected_amount
        assert data["environment"] == "test"
        assert "session_id" in data
        assert "checkout_url" in data
        assert data["checkout_url"].startswith("https://checkout.stripe.com/pay/")

    def test_checkout_spanish_language_returns_spanish_message(
        self, test_client: TestClient
    ):
        """Idioma 'es' debe devolver mensaje en español."""
        response = test_client.post(
            "/billing/checkout",
            json={
                "plan_id": "support_sos_1h",
                "customer_email": "cliente@empresa.de",
                "language": "es",
            },
        )
        assert "Sesión de pago creada" in response.json()["message"]
        assert "recibirá el enlace" in response.json()["message"]

    def test_checkout_german_language_returns_german_message(
        self, test_client: TestClient
    ):
        """Idioma 'de' debe devolver mensaje en alemán."""
        response = test_client.post(
            "/billing/checkout",
            json={
                "plan_id": "support_sos_1h",
                "customer_email": "cliente@empresa.de",
                "language": "de",
            },
        )
        assert "Stripe-Checkout-Sitzung" in response.json()["message"]
        assert "erhalten Sie" in response.json()["message"]

    def test_checkout_invalid_plan_id_is_rejected(self, test_client: TestClient):
        """Un plan desconocido debe devolver 400, nunca cobrar otro precio."""
        response = test_client.post(
            "/billing/checkout",
            json={
                "plan_id": "plan_inexistente",
                "customer_email": "cliente@empresa.de",
                "language": "es",
            },
        )
        assert response.status_code == 400
        assert "Plan desconocido" in response.json()["detail"]

    def test_checkout_with_missing_fields_uses_defaults(self, test_client: TestClient):
        """Campos faltantes usan valores por defecto del schema."""
        response = test_client.post("/billing/checkout", json={})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["plan_id"] == "support_sos_1h"  # Default del schema
        assert data["amount_eur"] == 65.00

    def test_checkout_response_schema(self, test_client: TestClient):
        """La respuesta debe coincidir con el esquema CheckoutResponse."""
        from app.schemas import CheckoutResponse

        response = test_client.post(
            "/billing/checkout",
            json={
                "plan_id": "support_sos_1h",
                "customer_email": "cliente@empresa.de",
                "language": "es",
            },
        )
        CheckoutResponse(**response.json())


class TestBillingWebhook:
    """Tests para POST /billing/webhook (Stripe webhook firmado)."""

    def test_webhook_with_valid_signature_is_accepted(
        self, test_client: TestClient, stripe_signature
    ):
        """Una firma correcta debe confirmar la recepción del evento."""
        body = b'{"event_id":"evt_test_123","event_type":"checkout.session.completed"}'
        response = test_client.post(
            "/billing/webhook",
            content=body,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": stripe_signature(body),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["received"] is True
        assert data["event_id"] == "evt_test_123"
        assert data["event_type"] == "checkout.session.completed"
        assert data["signature_present"] is True
        assert data["environment"] == "test"
        assert "action_taken" in data

    def test_webhook_rejects_missing_signature(self, test_client: TestClient):
        """Sin cabecera Stripe-Signature debe devolver 400."""
        response = test_client.post(
            "/billing/webhook",
            json={"event_id": "evt_test_456", "event_type": "payment_intent.succeeded"},
        )
        assert response.status_code == 400
        assert "Firma" in response.json()["detail"]

    def test_webhook_rejects_invalid_signature(self, test_client: TestClient):
        """Una firma que no coincide con el HMAC debe rechazarse."""
        body = b'{"event_id":"evt_test_456","event_type":"payment_intent.succeeded"}'
        response = test_client.post(
            "/billing/webhook",
            content=body,
            headers={"Stripe-Signature": "t=12345,v1=custom_signature"},
        )
        assert response.status_code == 400

    def test_webhook_rejects_tampered_body(
        self, test_client: TestClient, stripe_signature
    ):
        """Modificar el cuerpo después de firmar debe invalidar la firma."""
        signed_body = b'{"event_id":"evt_ok","event_type":"checkout.session.completed"}'
        header = stripe_signature(signed_body)
        tampered = b'{"event_id":"evt_ok","event_type":"invoice.paid"}'
        response = test_client.post(
            "/billing/webhook", content=tampered, headers={"Stripe-Signature": header}
        )
        assert response.status_code == 400

    def test_webhook_rejects_stale_timestamp(
        self, test_client: TestClient, stripe_signature
    ):
        """Un evento fuera de la ventana anti-replay debe rechazarse."""
        body = b'{"event_id":"evt_old","event_type":"checkout.session.completed"}'
        stale = stripe_signature(body, timestamp=1_000_000)
        response = test_client.post(
            "/billing/webhook", content=body, headers={"Stripe-Signature": stale}
        )
        assert response.status_code == 400

    def test_webhook_with_missing_fields_uses_defaults(
        self, test_client: TestClient, stripe_signature
    ):
        """Payload incompleto usa valores por defecto del schema."""
        body = b"{}"
        response = test_client.post(
            "/billing/webhook",
            content=body,
            headers={"Stripe-Signature": stripe_signature(body)},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["received"] is True
        assert data["event_id"] == "evt_mock_renatx_999"
        assert data["event_type"] == "checkout.session.completed"

    def test_webhook_response_schema(self, test_client: TestClient, stripe_signature):
        """La respuesta debe tener la estructura esperada."""
        from app.schemas import WebhookPayload

        body = b'{"event_id":"evt_test_789","event_type":"checkout.session.completed"}'
        response = test_client.post(
            "/billing/webhook",
            content=body,
            headers={"Stripe-Signature": stripe_signature(body)},
        )
        WebhookPayload(event_id="evt_test_789", event_type="checkout.session.completed")
        data = response.json()
        assert all(
            k in data for k in ["received", "event_id", "event_type", "environment"]
        )


class TestBillingWebhookMalformedPayload:
    def test_webhook_rejects_invalid_json_with_valid_signature(
        self, test_client: TestClient, stripe_signature
    ):
        """Una firma válida no salva un cuerpo que no es JSON."""
        body = b"esto-no-es-json"
        response = test_client.post(
            "/billing/webhook",
            content=body,
            headers={"Stripe-Signature": stripe_signature(body)},
        )
        assert response.status_code == 400
        assert "Payload" in response.json()["detail"]
