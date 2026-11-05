"""Tests para el hashing de contraseñas PBKDF2 (app.core.passwords)."""

import pytest

from app.core.passwords import hash_password, verify_password


class TestHashPassword:
    def test_hash_has_expected_format(self):
        encoded = hash_password("contraseña-segura", iterations=1000)
        algorithm, iterations, salt, digest = encoded.split("$")
        assert algorithm == "pbkdf2_sha256"
        assert int(iterations) == 1000
        assert len(bytes.fromhex(salt)) == 16
        assert len(bytes.fromhex(digest)) == 32

    def test_hash_never_contains_plaintext(self):
        encoded = hash_password("super-secreta", iterations=1000)
        assert "super-secreta" not in encoded

    def test_same_password_produces_different_hashes(self):
        """La sal aleatoria debe hacer únicos dos hashes de la misma clave."""
        assert hash_password("igual", iterations=1000) != hash_password(
            "igual", iterations=1000
        )

    def test_empty_password_rejected(self):
        with pytest.raises(ValueError):
            hash_password("")

    def test_too_long_password_rejected(self):
        with pytest.raises(ValueError):
            hash_password("x" * 2000)

    def test_iterations_out_of_range_rejected(self):
        with pytest.raises(ValueError):
            hash_password("clave", iterations=0)


class TestVerifyPassword:
    def test_correct_password_accepted(self):
        encoded = hash_password("linux-admin-demo", iterations=1000)
        assert verify_password("linux-admin-demo", encoded) is True

    def test_wrong_password_rejected(self):
        encoded = hash_password("linux-admin-demo", iterations=1000)
        assert verify_password("linux-admin-dem0", encoded) is False

    def test_malformed_hash_rejected_without_exception(self):
        for broken in ["", "pbkdf2_sha256", "otro$1$aa$bb", "pbkdf2_sha256$x$aa$bb"]:
            assert verify_password("clave", broken) is False

    def test_unknown_algorithm_rejected(self):
        encoded = hash_password("clave", iterations=1000).replace("pbkdf2_sha256", "md5", 1)
        assert verify_password("clave", encoded) is False

    def test_empty_password_rejected(self):
        encoded = hash_password("clave", iterations=1000)
        assert verify_password("", encoded) is False

    def test_out_of_range_iterations_in_hash_rejected(self):
        assert verify_password("clave", "pbkdf2_sha256$0$aa$bb") is False

    def test_empty_salt_or_digest_rejected(self):
        assert verify_password("clave", "pbkdf2_sha256$1000$$") is False
