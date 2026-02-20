"""Environment-driven configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass

from .exceptions import ConfigurationError

DEFAULT_BASE_URL = "https://testnet.binancefuture.com"
DEFAULT_LOG_FILE = "logs/trading_bot.log"


def _parse_positive_int(raw_value: str, env_name: str) -> int:
    """Parse positive integer from environment."""
    try:
        parsed = int(raw_value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{env_name} must be an integer.") from exc

    if parsed <= 0:
        raise ConfigurationError(f"{env_name} must be greater than 0.")
    return parsed


def _parse_positive_float(raw_value: str, env_name: str) -> float:
    """Parse positive float from environment."""
    try:
        parsed = float(raw_value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{env_name} must be a number.") from exc

    if parsed <= 0:
        raise ConfigurationError(f"{env_name} must be greater than 0.")
    return parsed


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    api_key: str
    api_secret: str
    base_url: str
    timeout_seconds: float
    max_retries: int
    backoff_seconds: float
    recv_window: int
    log_file: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Load and validate settings from environment."""
        api_key = os.getenv("BINANCE_API_KEY", "").strip()
        api_secret = os.getenv("BINANCE_API_SECRET", "").strip()

        if not api_key:
            raise ConfigurationError("BINANCE_API_KEY is required.")
        if not api_secret:
            raise ConfigurationError("BINANCE_API_SECRET is required.")

        base_url = os.getenv("BINANCE_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
        timeout_seconds = _parse_positive_float(
            os.getenv("BINANCE_TIMEOUT_SECONDS", "10"),
            "BINANCE_TIMEOUT_SECONDS",
        )
        max_retries = _parse_positive_int(
            os.getenv("BINANCE_MAX_RETRIES", "3"),
            "BINANCE_MAX_RETRIES",
        )
        backoff_seconds = _parse_positive_float(
            os.getenv("BINANCE_BACKOFF_SECONDS", "1"),
            "BINANCE_BACKOFF_SECONDS",
        )
        recv_window = _parse_positive_int(
            os.getenv("BINANCE_RECV_WINDOW", "5000"),
            "BINANCE_RECV_WINDOW",
        )
        log_file = os.getenv("LOG_FILE", DEFAULT_LOG_FILE).strip() or DEFAULT_LOG_FILE

        return cls(
            api_key=api_key,
            api_secret=api_secret,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            backoff_seconds=backoff_seconds,
            recv_window=recv_window,
            log_file=log_file,
        )
