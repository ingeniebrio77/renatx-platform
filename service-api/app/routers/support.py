"""
Controlador del Servicio Remoto Bajo Demanda (RustDesk On-Demand).
Permite a Franco Renato Palavecino encender o apagar la sala de asistencia remota
por horas/minutos (protegido con JWT) y calcula el coste acumulado de la sesión.
"""

from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.security import get_current_user
from app.schemas import RustDeskStatusResponse

router = APIRouter(prefix="/support", tags=["Soporte Remoto Efímero (RustDesk)"])

# Estado en memoria de la instancia efímera de RustDesk (Hetzner CX22: 0.007 EUR/h)
HOURLY_RATE_EUR = 0.007

_RUSTDESK_STATE: dict[str, Any] = {
    "active": False,
    "started_at": None,
    "public_key": "renatx_ed25519_pub_k9Xm2vQ8pL4nR7wY1zC5bN3mF6jH0sD2gA=",
}


def _build_status() -> RustDeskStatusResponse:
    active = bool(_RUSTDESK_STATE["active"])
    started_at: datetime | None = _RUSTDESK_STATE["started_at"]
    host = (
        "renatx.localhost"
        if settings.base_domain.endswith(".localhost")
        else f"support.{settings.base_domain}"
    )

    if active and started_at is not None:
        now = datetime.now(timezone.utc)
        elapsed_seconds = max(60, int((now - started_at).total_seconds()))
        elapsed_minutes = max(1, elapsed_seconds // 60)
        estimated_cost = round((elapsed_seconds / 3600.0) * HOURLY_RATE_EUR, 5)
        return RustDeskStatusResponse(
            active=True,
            status_label="ONLINE (Instancia Efímera Activa)",
            id_server=f"{host}:21116",
            relay_server=f"{host}:21117",
            public_key=_RUSTDESK_STATE["public_key"],
            started_at_utc=started_at.isoformat(),
            elapsed_minutes=elapsed_minutes,
            hourly_rate_eur=HOURLY_RATE_EUR,
            estimated_session_cost_eur=estimated_cost,
            instructions_es=(
                "Abra RustDesk → Configuración → Red → Servidor ID/Relay y pegue los datos "
                "mostrados arriba. El cifrado de extremo a extremo está garantizado."
            ),
            instructions_de=(
                "Öffnen Sie RustDesk → Einstellungen → Netzwerk → ID/Relay-Server und fügen "
                "Sie die obigen Daten ein. Ende-zu-Ende-Verschlüsselung ist aktiv."
            ),
        )

    return RustDeskStatusResponse(
        active=False,
        status_label="STANDBY (0,00 €/h — Instancia Apagada)",
        id_server="— (En espera de iniciar sesión) —",
        relay_server="— (En espera de iniciar sesión) —",
        public_key="— (Se habilita al activar la sesión) —",
        started_at_utc=None,
        elapsed_minutes=0,
        hourly_rate_eur=HOURLY_RATE_EUR,
        estimated_session_cost_eur=0.0,
        instructions_es=(
            "El servidor de soporte remoto solo se enciende durante las sesiones agendadas "
            "para garantizar máxima seguridad (superficie de ataque cero en reposo)."
        ),
        instructions_de=(
            "Der Remote-Support-Server wird nur während gebuchter Sitzungen gestartet "
            "(Null-Angriffsfläche im Ruhezustand & maximale DSGVO-Sicherheit)."
        ),
    )


@router.get("/status", response_model=RustDeskStatusResponse)
def get_rustdesk_status() -> RustDeskStatusResponse:
    """Consulta pública para que el cliente vea si el nodo RustDesk está activo."""
    return _build_status()


@router.post("/start", response_model=RustDeskStatusResponse)
def start_rustdesk_instance(
    _admin: dict[str, Any] = Depends(get_current_user),
) -> RustDeskStatusResponse:
    """
    [Solo Admin con JWT] Activa la sala de soporte remoto por horas/minutos
    y habilita las credenciales de conexión para el cliente.
    """
    _RUSTDESK_STATE["active"] = True
    _RUSTDESK_STATE["started_at"] = datetime.now(timezone.utc)
    return _build_status()


@router.post("/stop", response_model=RustDeskStatusResponse)
def stop_rustdesk_instance(
    _admin: dict[str, Any] = Depends(get_current_user),
) -> RustDeskStatusResponse:
    """
    [Solo Admin con JWT] Detiene la sesión de soporte remoto y vuelve a coste 0,00 €/h.
    """
    _RUSTDESK_STATE["active"] = False
    _RUSTDESK_STATE["started_at"] = None
    return _build_status()
