"""Validation utilities for CLI order input."""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Optional

from .exceptions import ValidationError
from .models import OrderInput

VALID_SIDES = {"BUY", "SELL"}
VALID_ORDER_TYPES = {"MARKET", "LIMIT"}
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9]{5,20}$")


@dataclass(frozen=True)
class ValidatedOrder:
    """Validated and normalized order fields."""

    symbol: str
    side: str
    order_type: str
    quantity: Decimal
    price: Optional[Decimal]


def validate_order_input(order_input: OrderInput) -> ValidatedOrder:
    """Validate and normalize raw CLI order input."""
    symbol = order_input.symbol.strip().upper()
    side = order_input.side.strip().upper()
    order_type = order_input.order_type.strip().upper()

    if not symbol:
        raise ValidationError("Symbol is required.")
    if not SYMBOL_PATTERN.fullmatch(symbol):
        raise ValidationError(
            f"Invalid symbol '{order_input.symbol}'. Use uppercase Binance symbols like BTCUSDT."
        )

    if side not in VALID_SIDES:
        raise ValidationError(f"Invalid side '{order_input.side}'. Allowed values: BUY or SELL.")

    if order_type not in VALID_ORDER_TYPES:
        raise ValidationError(
            f"Invalid order type '{order_input.order_type}'. Allowed values: MARKET or LIMIT."
        )

    quantity = _parse_positive_decimal(order_input.quantity, "quantity")
    price: Optional[Decimal] = None

    if order_type == "LIMIT":
        if order_input.price is None:
            raise ValidationError("Price is required for LIMIT orders. Provide --price.")
        price = _parse_positive_decimal(order_input.price, "price")
    elif order_input.price not in (None, ""):
        raise ValidationError("Price is only allowed for LIMIT orders. Remove --price for MARKET.")

    return ValidatedOrder(
        symbol=symbol,
        side=side,
        order_type=order_type,
        quantity=quantity,
        price=price,
    )


def _parse_positive_decimal(value: str, field_name: str) -> Decimal:
    """Parse and validate a positive decimal value."""
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError) as exc:
        raise ValidationError(f"Invalid {field_name} '{value}'. Must be a numeric value.") from exc

    if parsed <= 0:
        raise ValidationError(f"{field_name.capitalize()} must be greater than 0.")
    return parsed
