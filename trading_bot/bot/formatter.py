"""CLI output formatting utilities."""
from __future__ import annotations

from typing import List, Tuple

from .models import OrderRequest, OrderResult, format_decimal


def _format_rows(rows: List[Tuple[str, str]]) -> str:
    width = max(len(label) for label, _ in rows)
    return "\n".join(f"{label:<{width}} : {value}" for label, value in rows)


def format_order_request_summary(order: OrderRequest) -> str:
    """Format order request summary for terminal output."""
    rows = [
        ("Symbol", order.symbol),
        ("Side", order.side),
        ("Order Type", order.order_type),
        ("Quantity", format_decimal(order.quantity)),
        ("Price", format_decimal(order.price) if order.price is not None else "N/A"),
        ("Client Order ID", order.client_order_id),
    ]
    return (
        "============================================================\n"
        "ORDER REQUEST SUMMARY\n"
        "------------------------------------------------------------\n"
        f"{_format_rows(rows)}\n"
        "============================================================"
    )


def format_order_response(result: OrderResult) -> str:
    """Format order response details for terminal output."""
    rows = [
        ("Result", "SUCCESS"),
        ("Order ID", result.order_id),
        ("Status", result.status),
        ("Executed Qty", format_decimal(result.executed_qty)),
        ("Average Price", format_decimal(result.avg_price) if result.avg_price is not None else "N/A"),
    ]
    return (
        "============================================================\n"
        "ORDER EXECUTION RESULT\n"
        "------------------------------------------------------------\n"
        f"{_format_rows(rows)}\n"
        "============================================================"
    )


def format_failure(error_type: str, message: str) -> str:
    """Format clear failure output."""
    rows = [("Result", "FAILURE"), ("Error Type", error_type), ("Message", message)]
    return (
        "============================================================\n"
        "ORDER EXECUTION FAILED\n"
        "------------------------------------------------------------\n"
        f"{_format_rows(rows)}\n"
        "============================================================"
    )
