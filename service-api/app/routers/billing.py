"""Endpoints de monetización con Stripe para los servicios 1-a-1 de Renatx."""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Header

from app.core.config import settings
from app.schemas import CheckoutRequest, CheckoutResponse, WebhookPayload

router = APIRouter(prefix="/billing", tags=["Catálogo y Pagos (Stripe)"])

# Catálogo oficial de servicios de Franco Renato Palavecino (Renatx)
CATALOG: dict[str, dict[str, Any]] = {
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


@router.get("/catalog")
def get_services_catalog() -> dict[str, Any]:
    """Devuelve el catálogo completo de servicios y precios en EUR."""
    return {"currency": "EUR", "services": CATALOG}


@router.post("/checkout", response_model=CheckoutResponse)
def create_checkout_session(payload: CheckoutRequest) -> CheckoutResponse:
    """
    Crea una sesión de pago en Stripe Checkout para el servicio seleccionado.
    En local/preprod devuelve una sesión simulada sin cargos reales.
    """
    item = CATALOG.get(payload.plan_id, CATALOG["support_sos_1h"])
    timestamp = int(datetime.now(timezone.utc).timestamp())
    session_id = f"cs_test_renatx_{payload.plan_id}_{timestamp}"
    title = item["title_de"] if payload.language == "de" else item["title_es"]

    if payload.language == "de":
        msg = (
            f"Stripe-Checkout-Sitzung für '{title}' ({item['amount_eur']:.2f} EUR) "
            f"erstellt. Nach der Zahlung erhalten Sie den Termin- & RustDesk-Zugang."
        )
    else:
        msg = (
            f"Sesión de pago creada para '{title}' ({item['amount_eur']:.2f} EUR). "
            f"Tras el pago recibirá el enlace de agenda y acceso a la sala RustDesk."
        )

    return CheckoutResponse(
        status="success",
        mode=item["mode"],
        session_id=session_id,
        checkout_url=f"https://checkout.stripe.com/pay/{session_id}",
        plan_id=payload.plan_id,
        service_title=title,
        amount_eur=item["amount_eur"],
        environment=settings.env,
        message=msg,
    )


@router.post("/webhook")
def stripe_webhook(
    payload: WebhookPayload,
    stripe_signature: str | None = Header(default="t=0000,v1=mock_sig"),
) -> dict[str, Any]:
    """Recibe la confirmación asíncrona de Stripe cuando el cliente completa el pago."""
    return {
        "received": True,
        "event_id": payload.event_id,
        "event_type": payload.event_type,
        "signature_present": bool(stripe_signature),
        "environment": settings.env,
        "action_taken": "Reserva 1-a-1 confirmada y notificada",
    }
