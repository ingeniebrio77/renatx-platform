"""
Tests para los esquemas Pydantic (validación de entrada y salida).
"""

import pytest
from pydantic import ValidationError

from app.schemas import (
    CheckoutRequest,
    CheckoutResponse,
    LoginRequest,
    RustDeskStatusResponse,
    TokenResponse,
    WebhookPayload,
)


class TestLoginRequestSchema:
    """Tests para LoginRequest."""

    def test_valid_login_request(self):
        data = LoginRequest(username="test@renatx.com", password="secret123")
        assert data.username == "test@renatx.com"
        assert data.password == "secret123"

    def test_login_request_defaults(self):
        data = LoginRequest()
        assert data.username == "renato@renatx.com"
        assert data.password == "linux-admin-demo"

    def test_login_request_accepts_extra_fields(self):
        """Pydantic v2 por defecto ignora campos extra (extra='ignore' en config)."""
        # En este caso LoginRequest no tiene extra='ignore' explícito,
        # pero hereda de BaseModel que por defecto es 'ignore'
        data = LoginRequest(username="test@test.com", password="pass", extra_field="ignored")
        assert data.username == "test@test.com"

    def test_login_request_empty_username_allowed_by_schema(self):
        """El schema permite username vacío (la validación de negocio está en el endpoint)."""
        data = LoginRequest(username="", password="password123")
        assert data.username == ""


class TestTokenResponseSchema:
    """Tests para TokenResponse."""

    def test_valid_token_response(self):
        data = TokenResponse(
            access_token="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            expires_in_minutes=60,
            environment="test",
        )
        assert data.token_type == "bearer"
        assert data.expires_in_minutes == 60
        assert data.environment == "test"

    def test_token_response_defaults(self):
        data = TokenResponse(
            access_token="token123",
            expires_in_minutes=30,
            environment="local",
        )
        assert data.token_type == "bearer"

    def test_token_response_missing_required_fails(self):
        with pytest.raises(ValidationError):
            TokenResponse(expires_in_minutes=60, environment="test")


class TestCheckoutRequestSchema:
    """Tests para CheckoutRequest."""

    def test_valid_checkout_request(self):
        data = CheckoutRequest(
            plan_id="support_sos_1h",
            customer_email="cliente@empresa.de",
            language="es",
        )
        assert data.plan_id == "support_sos_1h"
        assert data.customer_email == "cliente@empresa.de"
        assert data.language == "es"

    def test_checkout_request_defaults(self):
        data = CheckoutRequest()
        assert data.plan_id == "support_sos_1h"
        assert data.customer_email == "cliente@empresa.de"
        assert data.language == "es"

    def test_checkout_request_invalid_email_allowed(self):
        """El schema no valida formato de email (validación en endpoint si se desea)."""
        data = CheckoutRequest(customer_email="no-es-email")
        assert data.customer_email == "no-es-email"

    def test_checkout_request_language_not_restricted(self):
        """El schema no restringe idiomas (validación en endpoint)."""
        data = CheckoutRequest(language="fr")
        assert data.language == "fr"


class TestCheckoutResponseSchema:
    """Tests para CheckoutResponse."""

    def test_valid_checkout_response(self):
        data = CheckoutResponse(
            status="success",
            mode="payment",
            session_id="cs_test_123",
            checkout_url="https://checkout.stripe.com/pay/cs_test_123",
            plan_id="support_sos_1h",
            service_title="Soporte Remoto S.O.S.",
            amount_eur=65.00,
            environment="test",
            message="Sesión creada correctamente",
        )
        assert data.status == "success"
        assert data.amount_eur == 65.00

    def test_checkout_response_all_fields_required(self):
        with pytest.raises(ValidationError):
            CheckoutResponse(
                status="success",
                mode="payment",
                session_id="cs_test_123",
                # Falta checkout_url
                plan_id="support_sos_1h",
                service_title="Test",
                amount_eur=65.00,
                environment="test",
                message="Test",
            )


class TestWebhookPayloadSchema:
    """Tests para WebhookPayload."""

    def test_valid_webhook_payload(self):
        data = WebhookPayload(
            event_id="evt_123",
            event_type="checkout.session.completed",
        )
        assert data.event_id == "evt_123"
        assert data.event_type == "checkout.session.completed"

    def test_webhook_payload_defaults(self):
        data = WebhookPayload()
        assert data.event_id == "evt_mock_renatx_999"
        assert data.event_type == "checkout.session.completed"


class TestRustDeskStatusResponseSchema:
    """Tests para RustDeskStatusResponse."""

    def test_valid_standby_response(self):
        data = RustDeskStatusResponse(
            active=False,
            status_label="STANDBY (0,00 €/h — Instancia Apagada)",
            id_server="— (En espera de iniciar sesión) —",
            relay_server="— (En espera de iniciar sesión) —",
            public_key="— (Se habilita al activar la sesión) —",
            started_at_utc=None,
            elapsed_minutes=0,
            hourly_rate_eur=0.007,
            estimated_session_cost_eur=0.0,
            instructions_es="Instrucciones en español",
            instructions_de="Anweisungen auf Deutsch",
        )
        assert data.active is False
        assert data.elapsed_minutes == 0
        assert data.estimated_session_cost_eur == 0.0

    def test_valid_active_response(self):
        data = RustDeskStatusResponse(
            active=True,
            status_label="ONLINE (Instancia Efímera Activa)",
            id_server="renatx.localhost:21116",
            relay_server="renatx.localhost:21117",
            public_key="renatx_ed25519_pub_k9Xm2vQ8pL4nR7wY1zC5bN3mF6jH0sD2gA=",
            started_at_utc="2026-10-30T10:00:00+00:00",
            elapsed_minutes=5,
            hourly_rate_eur=0.007,
            estimated_session_cost_eur=0.00058,
            instructions_es="Instrucciones en español",
            instructions_de="Anweisungen auf Deutsch",
        )
        assert data.active is True
        assert data.elapsed_minutes == 5
        assert data.estimated_session_cost_eur > 0

    def test_rustdesk_status_all_fields_required(self):
        with pytest.raises(ValidationError):
            RustDeskStatusResponse(
                active=True,
                status_label="ONLINE",
                id_server="host:port",
                relay_server="host:port",
                public_key="key",
                # Falta started_at_utc
                elapsed_minutes=1,
                hourly_rate_eur=0.007,
                estimated_session_cost_eur=0.001,
                instructions_es="es",
                instructions_de="de",
            )


class TestSchemaEdgeCases:
    """Tests de casos borde para esquemas."""

    def test_amount_eur_accepts_float(self):
        """amount_eur debe aceptar float."""
        from app.schemas import CheckoutResponse

        data = CheckoutResponse(
            status="success",
            mode="payment",
            session_id="cs_test",
            checkout_url="https://test.com",
            plan_id="test",
            service_title="Test",
            amount_eur=49.99,
            environment="test",
            message="Test",
        )
        assert data.amount_eur == 49.99

    def test_amount_eur_coerces_string_to_float(self):
        """Pydantic v2 coacciona string numérico a float (comportamiento por defecto)."""
        from app.schemas import CheckoutResponse

        data = CheckoutResponse(
            status="success",
            mode="payment",
            session_id="cs_test",
            checkout_url="https://test.com",
            plan_id="test",
            service_title="Test",
            amount_eur="49.99",  # String que se coacciona a float
            environment="test",
            message="Test",
        )
        assert data.amount_eur == 49.99
        assert isinstance(data.amount_eur, float)

    def test_amount_eur_rejects_non_numeric_string(self):
        """String no numérico debe fallar."""
        from app.schemas import CheckoutResponse

        with pytest.raises(ValidationError):
            CheckoutResponse(
                status="success",
                mode="payment",
                session_id="cs_test",
                checkout_url="https://test.com",
                plan_id="test",
                service_title="Test",
                amount_eur="no-es-numero",
                environment="test",
                message="Test",
            )

    def test_elapsed_minutes_accepts_zero_and_positive(self):
        """elapsed_minutes debe aceptar 0 y positivos."""
        from app.schemas import RustDeskStatusResponse

        for minutes in [0, 1, 60, 1440]:
            data = RustDeskStatusResponse(
                active=True,
                status_label="ONLINE",
                id_server="h:p",
                relay_server="h:p",
                public_key="k",
                started_at_utc="2026-10-30T10:00:00+00:00",
                elapsed_minutes=minutes,
                hourly_rate_eur=0.007,
                estimated_session_cost_eur=0.001,
                instructions_es="es",
                instructions_de="de",
            )
            assert data.elapsed_minutes == minutes

    def test_elapsed_minutes_negative_allowed_by_pydantic(self):
        """Pydantic no valida negativos por defecto para int (requiere Field(ge=0))."""
        from app.schemas import RustDeskStatusResponse

        # Esto NO falla en Pydantic v2 sin validación explícita
        data = RustDeskStatusResponse(
            active=True,
            status_label="ONLINE",
            id_server="h:p",
            relay_server="h:p",
            public_key="k",
            started_at_utc="2026-10-30T10:00:00+00:00",
            elapsed_minutes=-1,  # Negativo - permitido sin Field(ge=0)
            hourly_rate_eur=0.007,
            estimated_session_cost_eur=0.001,
            instructions_es="es",
            instructions_de="de",
        )
        assert data.elapsed_minutes == -1