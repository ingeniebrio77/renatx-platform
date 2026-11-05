"""
Hashing de contraseñas con PBKDF2-HMAC-SHA256 (biblioteca estándar).

Formato almacenado (una sola línea, apta para una variable de entorno):

    pbkdf2_sha256$<iteraciones>$<salt_hex>$<hash_hex>

Para generar un hash nuevo:

    make password-hash

Nunca se guarda la contraseña en claro ni se compara con `==`
(se usa `hmac.compare_digest` para evitar ataques de temporización).
"""

import hashlib
import hmac
import secrets

ALGORITHM = "pbkdf2_sha256"
DEFAULT_ITERATIONS = 260_000
SALT_BYTES = 16
MAX_PASSWORD_LENGTH = 1024
MAX_ITERATIONS = 5_000_000


def hash_password(password: str, *, iterations: int = DEFAULT_ITERATIONS) -> str:
    """Devuelve el hash salado de `password` en el formato documentado."""
    if not isinstance(password, str) or not password:
        raise ValueError("La contraseña no puede estar vacía")
    if len(password) > MAX_PASSWORD_LENGTH:
        raise ValueError(f"La contraseña supera {MAX_PASSWORD_LENGTH} caracteres")
    if not 1 <= iterations <= MAX_ITERATIONS:
        raise ValueError("Número de iteraciones fuera de rango")

    salt = secrets.token_bytes(SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"{ALGORITHM}${iterations}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    """Comprueba `password` contra un hash generado por `hash_password`.

    Devuelve `False` ante cualquier hash malformado en lugar de lanzar,
    para que un fallo de configuración no se convierta en un 500.
    """
    if not password or not encoded or len(password) > MAX_PASSWORD_LENGTH:
        return False

    try:
        algorithm, iterations_raw, salt_hex, digest_hex = encoded.split("$", 3)
        if algorithm != ALGORITHM:
            return False
        iterations = int(iterations_raw)
        if not 1 <= iterations <= MAX_ITERATIONS:
            return False
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(digest_hex)
        if not salt or not expected:
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
        )
    except (ValueError, AttributeError, UnicodeEncodeError):
        return False

    return hmac.compare_digest(candidate, expected)


if __name__ == "__main__":  # pragma: no cover - utilidad de línea de comandos
    import getpass
    import sys

    first = getpass.getpass("Contraseña de administrador: ")
    second = getpass.getpass("Repite la contraseña: ")
    if first != second:
        sys.exit("Las contraseñas no coinciden")
    if len(first) < 12:
        sys.exit("Usa al menos 12 caracteres")
    print()
    print("Copia esta línea en tu .env:")
    print(f"ADMIN_PASSWORD_HASH={hash_password(first)}")
