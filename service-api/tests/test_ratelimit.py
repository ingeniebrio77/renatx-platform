"""Tests para el limitador de peticiones en memoria (app.core.ratelimit)."""

import time

import pytest

from app.core.ratelimit import SlidingWindowRateLimiter


class TestSlidingWindowRateLimiter:
    def test_allows_up_to_max_attempts(self):
        limiter = SlidingWindowRateLimiter(max_attempts=3, window_seconds=60)
        assert [limiter.allow("ip") for _ in range(3)] == [True, True, True]

    def test_blocks_after_max_attempts(self):
        limiter = SlidingWindowRateLimiter(max_attempts=2, window_seconds=60)
        assert limiter.allow("ip") is True
        assert limiter.allow("ip") is True
        assert limiter.allow("ip") is False

    def test_keys_are_independent(self):
        limiter = SlidingWindowRateLimiter(max_attempts=1, window_seconds=60)
        assert limiter.allow("a") is True
        assert limiter.allow("b") is True
        assert limiter.allow("a") is False

    def test_window_expiry_allows_again(self, monkeypatch):
        limiter = SlidingWindowRateLimiter(max_attempts=1, window_seconds=10)
        now = time.monotonic()
        monkeypatch.setattr("app.core.ratelimit.time.monotonic", lambda: now)
        assert limiter.allow("ip") is True
        assert limiter.allow("ip") is False

        monkeypatch.setattr("app.core.ratelimit.time.monotonic", lambda: now + 11)
        assert limiter.allow("ip") is True

    def test_reset_clears_counters(self):
        limiter = SlidingWindowRateLimiter(max_attempts=1, window_seconds=60)
        assert limiter.allow("ip") is True
        assert limiter.allow("ip") is False
        limiter.reset()
        assert limiter.allow("ip") is True

    def test_invalid_configuration_rejected(self):
        with pytest.raises(ValueError):
            SlidingWindowRateLimiter(max_attempts=0, window_seconds=60)
        with pytest.raises(ValueError):
            SlidingWindowRateLimiter(max_attempts=1, window_seconds=0)

    def test_properties_exposed(self):
        limiter = SlidingWindowRateLimiter(max_attempts=5, window_seconds=300)
        assert limiter.max_attempts == 5
        assert limiter.window_seconds == 300

    def test_prune_removes_stale_keys(self, monkeypatch):
        """La limpieza oportunista no debe romper con claves frías."""
        limiter = SlidingWindowRateLimiter(max_attempts=1, window_seconds=1)
        now = time.monotonic()
        monkeypatch.setattr("app.core.ratelimit.time.monotonic", lambda: now)
        assert limiter.allow("a") is True

        monkeypatch.setattr("app.core.ratelimit.time.monotonic", lambda: now + 10)
        # Fuerza la ruta de limpieza creando muchas claves
        for i in range(10_001):
            limiter.allow(f"key-{i}")
        assert limiter.allow("nueva") is True
