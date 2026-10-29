"""Esquemas Pydantic (Tipado de entrada y salida de datos JSON)."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Datos recibidos al iniciar sesión."""

    username: str = Field(default="renato@renatx.com", examples=["renato@renatx.com"])
    password: str = Field(default="linux-admin-demo", examples=["linux-admin-demo"])


class TokenResponse(BaseModel):
    """Respuesta con el token JWT emitido."""

    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    environment: str


class CheckoutRequest(BaseModel):
    """Petición para reservar y pagar un servicio 1-a-1 o bono en Stripe."""

    plan_id: str = Field(
        default="support_sos_1h",
        description="ID del servicio: support_sos_1h | mentoring_1h | devops_pack_5h",
    )
    customer_email: str = Field(default="cliente@empresa.de", description="Email del cliente/alumno")
    language: str = Field(default="es", description="Idioma de la sesión (es | de)")


class CheckoutResponse(BaseModel):
    """Respuesta simulada de Stripe Checkout."""

    status: str
    mode: str
    session_id: str
    checkout_url: str
    plan_id: str
    service_title: str
    amount_eur: float
    environment: str
    message: str


class WebhookPayload(BaseModel):
    """Estructura base de un evento Webhook enviado por Stripe."""

    event_id: str = Field(default="evt_mock_renatx_999")
    event_type: str = Field(default="checkout.session.completed")


class RustDeskStatusResponse(BaseModel):
    """Estado en tiempo real de la instancia efímera de soporte remoto RustDesk."""

    active: bool
    status_label: str
    id_server: str
    relay_server: str
    public_key: str
    started_at_utc: str | None
    elapsed_minutes: int
    hourly_rate_eur: float
    estimated_session_cost_eur: float
    instructions_es: str
    instructions_de: str
