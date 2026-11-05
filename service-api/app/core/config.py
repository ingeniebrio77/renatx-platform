"""
Configuración centralizada de la API (Pydantic Settings).
Lee las variables de entorno definidas en `.env` o inyectadas por Podman.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

# Valor de ejemplo publicado en el repositorio: nunca debe llegar a producción.
INSECURE_JWT_SECRETS = {
    "",
    "super_secret_dev_key_renatx_2026_change_in_prod",
}

MIN_JWT_SECRET_LENGTH = 32
PASSWORD_HASH_PREFIX = "pbkdf2_sha256$"


class Settings(BaseSettings):
    """Parámetros globales del backend de Renatx."""

    app_name: str = "Renatx Platform API"
    owner: str = "Franco Renato Palavecino (Hamburg, DE)"
    env: str = "local"
    base_domain: str = "renatx.localhost"

    # PostgreSQL (Red interna db_net)
    postgres_user: str = "renatx_admin"
    postgres_password: str = "renatx_local_dev_password_change_me"
    postgres_db: str = "renatx_db"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    # Autenticación JWT
    jwt_secret_key: str = "super_secret_dev_key_renatx_2026_change_in_prod"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # Credenciales del panel de instructor (usuario único + hash PBKDF2)
    admin_username: str = "renato@renatx.com"
    admin_password_hash: str = ""

    # Límite de intentos de login por IP
    login_rate_limit_attempts: int = 5
    login_rate_limit_window_seconds: int = 300

    # CORS: lista separada por comas. En producción el mismo origen (Traefik)
    # hace que el navegador no necesite CORS, pero se permite configurarlo.
    cors_origins: str = "http://renatx.localhost:8080,http://localhost:3000"

    # Documentación interactiva: por defecto desactivada en producción.
    enable_docs: bool | None = None

    # Monetización Stripe (Mock)
    stripe_secret_key: str = "sk_test_mock_renatx_000000000000"
    stripe_webhook_secret: str = "whsec_mock_renatx_000000000000"
    stripe_price_id_pro: str = "price_mock_renatx_pro_monthly"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        """Orígenes permitidos como lista limpia."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def docs_enabled(self) -> bool:
        """`/docs` y `/openapi.json` disponibles (off en producción por defecto)."""
        if self.enable_docs is not None:
            return self.enable_docs
        return self.env != "prod"

    def security_problems(self) -> list[str]:
        """Lista de configuraciones inseguras que impiden arrancar en producción."""
        problems: list[str] = []

        if (
            self.jwt_secret_key in INSECURE_JWT_SECRETS
            or len(self.jwt_secret_key) < MIN_JWT_SECRET_LENGTH
        ):
            problems.append(
                f"JWT_SECRET_KEY ausente, de ejemplo o con menos de "
                f"{MIN_JWT_SECRET_LENGTH} caracteres"
            )

        if not self.admin_password_hash.startswith(PASSWORD_HASH_PREFIX):
            problems.append(
                "ADMIN_PASSWORD_HASH no configurado (genera uno con `make password-hash`)"
            )

        if self.stripe_webhook_secret.startswith("whsec_mock"):
            problems.append("STRIPE_WEBHOOK_SECRET sigue siendo el valor de ejemplo")

        if self.base_domain.endswith(".localhost"):
            problems.append("BASE_DOMAIN sigue apuntando a localhost")

        return problems


settings = Settings()
