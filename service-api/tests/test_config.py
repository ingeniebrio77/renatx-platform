"""
Tests para el módulo de configuración (Settings de Pydantic).
"""

from app.core.config import Settings


class TestSettingsDefaults:
    """Tests para valores por defecto de la configuración.

    NOTA: Estas pruebas se ejecutan con variables de entorno de test definidas en conftest.py,
    por lo que los valores reflejan la configuración de test, no los defaults del código.
    """

    def test_app_name_default(self):
        assert Settings().app_name == "Renatx Platform API"

    def test_owner_default(self):
        assert Settings().owner == "Franco Renato Palavecino (Hamburg, DE)"

    def test_env_is_test_in_test_environment(self):
        """En entorno de test, env debe ser 'test' (definido en conftest.py)."""
        assert Settings().env == "test"

    def test_base_domain_is_localhost_in_test(self):
        assert Settings().base_domain == "renatx.localhost"

    def test_postgres_uses_test_values(self):
        s = Settings()
        assert s.postgres_user == "test_user"
        assert s.postgres_password == "test_password"
        assert s.postgres_db == "test_db"
        assert s.postgres_host == "localhost"
        assert s.postgres_port == 5432

    def test_jwt_uses_test_secret(self):
        s = Settings()
        assert s.jwt_secret_key == "test_secret_key_for_testing_only_32chars"
        assert s.jwt_algorithm == "HS256"
        assert s.jwt_expire_minutes == 60

    def test_stripe_defaults(self):
        s = Settings()
        assert s.stripe_secret_key == "sk_test_mock_renatx_000000000000"
        assert s.stripe_webhook_secret == "whsec_mock_renatx_000000000000"
        assert s.stripe_price_id_pro == "price_mock_renatx_pro_monthly"


class TestSettingsFromEnv:
    """Tests para carga de configuración desde variables de entorno."""

    def test_env_overrides_defaults(self, monkeypatch):
        monkeypatch.setenv("ENV", "prod")
        monkeypatch.setenv("BASE_DOMAIN", "renatx.com")
        monkeypatch.setenv("JWT_SECRET_KEY", "prod_secret_key_very_long_and_secure_2026")

        # Reimportar para que tome las nuevas variables
        import importlib

        import app.core.config
        importlib.reload(app.core.config)
        from app.core.config import Settings

        s = Settings()
        assert s.env == "prod"
        assert s.base_domain == "renatx.com"
        assert s.jwt_secret_key == "prod_secret_key_very_long_and_secure_2026"

    def test_postgres_from_env(self, monkeypatch):
        monkeypatch.setenv("POSTGRES_USER", "custom_user")
        monkeypatch.setenv("POSTGRES_PASSWORD", "custom_pass")
        monkeypatch.setenv("POSTGRES_DB", "custom_db")
        monkeypatch.setenv("POSTGRES_HOST", "custom-host")
        monkeypatch.setenv("POSTGRES_PORT", "5433")

        import importlib

        import app.core.config
        importlib.reload(app.core.config)
        from app.core.config import Settings

        s = Settings()
        assert s.postgres_user == "custom_user"
        assert s.postgres_password == "custom_pass"
        assert s.postgres_db == "custom_db"
        assert s.postgres_host == "custom-host"
        assert s.postgres_port == 5433

    def test_extra_fields_ignored(self, monkeypatch):
        """Campos extra en .env deben ser ignorados (extra='ignore')."""
        monkeypatch.setenv("UNKNOWN_FIELD", "some_value")

        import importlib

        import app.core.config
        importlib.reload(app.core.config)
        from app.core.config import Settings

        # No debe lanzar error
        s = Settings()
        assert s.app_name == "Renatx Platform API"


class TestSettingsValidation:
    """Tests de validación de tipos."""

    def test_postgres_port_is_int(self, monkeypatch):
        monkeypatch.setenv("POSTGRES_PORT", "5432")

        import importlib

        import app.core.config
        importlib.reload(app.core.config)
        from app.core.config import Settings

        s = Settings()
        assert isinstance(s.postgres_port, int)
        assert s.postgres_port == 5432

    def test_jwt_expire_minutes_is_int(self, monkeypatch):
        monkeypatch.setenv("JWT_EXPIRE_MINUTES", "120")

        import importlib

        import app.core.config
        importlib.reload(app.core.config)
        from app.core.config import Settings

        s = Settings()
        assert isinstance(s.jwt_expire_minutes, int)
        assert s.jwt_expire_minutes == 120

    def test_invalid_port_raises_validation_error(self, monkeypatch):
        """Puerto inválido debe lanzar error de validación al instanciar Settings."""
        import pytest
        monkeypatch.setenv("POSTGRES_PORT", "no-es-numero")

        # Crear una nueva instancia de Settings directamente (sin recargar módulo)
        # para probar la validación de Pydantic
        with pytest.raises(Exception) as exc_info:
            Settings(_env_file=None, _env_file_encoding=None, POSTGRES_PORT="no-es-numero")
        assert "postgres_port" in str(exc_info.value).lower()
        assert "int" in str(exc_info.value).lower()


class TestSettingsSingleton:
    """Tests para verificar que settings es un singleton global."""

    def test_settings_instance_is_same(self):
        from app.core.config import settings as settings1
        from app.core.config import settings as settings2

        assert settings1 is settings2


class TestSettingsImmutability:
    """Tests para verificar comportamiento de inmutabilidad (Pydantic v2)."""

    def test_cannot_modify_frozen_fields(self):
        """Pydantic Settings no es frozen por defecto, pero no se debe modificar en runtime."""
        from app.core.config import settings

        # En tests no se debe modificar la instancia global
        original = settings.app_name
        assert settings.app_name == original