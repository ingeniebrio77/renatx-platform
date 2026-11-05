"""
Limitador de peticiones en memoria (ventana deslizante).

Pensado para endpoints sensibles con un único proceso (uvicorn sin `--workers`).
Si algún día se escala horizontalmente, sustituir por Redis o el rate-limit
de Traefik: este módulo no se comparte entre procesos.
"""

import threading
import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    """Permite como máximo `max_attempts` eventos por clave en `window_seconds`."""

    def __init__(self, max_attempts: int, window_seconds: int) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts debe ser >= 1")
        if window_seconds < 1:
            raise ValueError("window_seconds debe ser >= 1")
        self._max_attempts = max_attempts
        self._window = window_seconds
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    @property
    def max_attempts(self) -> int:
        return self._max_attempts

    @property
    def window_seconds(self) -> int:
        return self._window

    def allow(self, key: str) -> bool:
        """Registra un intento y devuelve si está dentro del límite."""
        now = time.monotonic()
        with self._lock:
            bucket = self._events[key]
            while bucket and now - bucket[0] > self._window:
                bucket.popleft()

            if len(bucket) >= self._max_attempts:
                return False

            bucket.append(now)
            if len(self._events) > 10_000:  # limpieza oportunista de claves frías
                self._prune(now)
            return True

    def reset(self) -> None:
        """Vacía todos los contadores (usado por los tests)."""
        with self._lock:
            self._events.clear()

    def _prune(self, now: float) -> None:
        stale = [
            key
            for key, bucket in self._events.items()
            if not bucket or now - bucket[-1] > self._window
        ]
        for key in stale:
            del self._events[key]
