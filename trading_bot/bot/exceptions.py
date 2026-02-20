"""Custom exceptions for trading bot."""
from __future__ import annotations

from typing import Any, Dict, Optional


class TradingBotError(Exception):
    """Base exception type for this project."""


class ValidationError(TradingBotError):
    """Raised when CLI input is invalid."""


class ConfigurationError(TradingBotError):
    """Raised when required environment settings are missing or invalid."""


class NetworkError(TradingBotError):
    """Raised when a network error occurs after retries."""

    def __init__(self, message: str, attempts: int) -> None:
        super().__init__(message)
        self.attempts = attempts


class APIError(TradingBotError):
    """Raised when Binance API returns an error."""

    def __init__(
        self,
        status_code: int,
        error_code: Optional[int],
        message: str,
        response_payload: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.response_payload = response_payload or {}

    def __str__(self) -> str:
        prefix = f"HTTP {self.status_code}"
        if self.error_code is not None:
            prefix += f" | Binance code {self.error_code}"
        return f"{prefix}: {self.message}"
