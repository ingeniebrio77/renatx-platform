"""
Configuración centralizada de la API (Pydantic Settings).
Lee las variables de entorno definidas en `.env` o inyectadas por Podman.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Monetización Stripe (Mock)
    stripe_secret_key: str = "sk_test_mock_renatx_000000000000"
    stripe_webhook_secret: str = "whsec_mock_renatx_000000000000"
    stripe_price_id_pro: str = "price_mock_renatx_pro_monthly"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
