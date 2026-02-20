"""Data models used by order flow."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional


def format_decimal(value: Decimal) -> str:
    """Render Decimal to plain string without scientific notation."""
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


@dataclass(frozen=True)
class OrderInput:
    """Raw input model from CLI."""

    symbol: str
    side: str
    order_type: str
    quantity: str
    price: Optional[str] = None


@dataclass(frozen=True)
class OrderRequest:
    """Validated order request model."""

    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Optional[Decimal]
    client_order_id: str

    def to_api_payload(self) -> Dict[str, str]:
        """Convert order request to Binance API payload."""
        payload: Dict[str, str] = {
            "symbol": self.symbol,
            "side": self.side,
            "type": self.order_type,
            "quantity": format_decimal(self.quantity),
            "newOrderRespType": "RESULT",
            "newClientOrderId": self.client_order_id,
        }

        if self.order_type == "LIMIT":
            payload["price"] = format_decimal(self.price or Decimal("0"))
            payload["timeInForce"] = "GTC"

        return payload


@dataclass(frozen=True)
class OrderResult:
    """Normalized order response fields used by CLI output."""

    order_id: str
    status: str
    executed_qty: Decimal
    avg_price: Optional[Decimal]
    symbol: str
    side: str
    order_type: str
    raw_payload: Dict[str, Any]

    @classmethod
    def from_api_response(cls, payload: Dict[str, Any]) -> "OrderResult":
        """Build result from Binance response payload."""
        return cls(
            order_id=str(payload.get("orderId", "N/A")),
            status=str(payload.get("status", "UNKNOWN")),
            executed_qty=_to_decimal(payload.get("executedQty", "0")),
            avg_price=_to_optional_decimal(payload.get("avgPrice")),
            symbol=str(payload.get("symbol", "")),
            side=str(payload.get("side", "")),
            order_type=str(payload.get("type", "")),
            raw_payload=payload,
        )


def _to_decimal(value: Any) -> Decimal:
    """Safely parse value into Decimal with fallback 0."""
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return Decimal("0")


def _to_optional_decimal(value: Any) -> Optional[Decimal]:
    """Safely parse optional Decimal values."""
    if value in (None, "", "0", "0.0"):
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
