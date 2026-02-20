"""Order orchestration layer."""
from __future__ import annotations

import logging
import time
import uuid

from .client import BinanceFuturesClient
from .models import OrderInput, OrderRequest, OrderResult
from .validators import validate_order_input


class OrderService:
    """Service layer responsible for validation + API execution."""

    def __init__(self, client: BinanceFuturesClient, logger: logging.Logger) -> None:
        self._client = client
        self._logger = logger

    def create_order_request(self, order_input: OrderInput) -> OrderRequest:
        """Validate raw order input and convert to OrderRequest."""
        validated = validate_order_input(order_input)
        client_order_id = self._generate_client_order_id()

        order_request = OrderRequest(
            symbol=validated.symbol,
            side=validated.side,
            order_type=validated.order_type,
            quantity=validated.quantity,
            price=validated.price,
            client_order_id=client_order_id,
        )

        self._logger.info(
            "order_validated | symbol=%s side=%s type=%s quantity=%s price=%s clientOrderId=%s",
            order_request.symbol,
            order_request.side,
            order_request.order_type,
            order_request.quantity,
            order_request.price,
            order_request.client_order_id,
        )
        return order_request

    def place_order(self, order_request: OrderRequest) -> OrderResult:
        """Submit order to Binance and normalize response."""
        api_payload = order_request.to_api_payload()
        response = self._client.place_order(api_payload)
        result = OrderResult.from_api_response(response)

        self._logger.info(
            "order_placed | orderId=%s status=%s executedQty=%s avgPrice=%s",
            result.order_id,
            result.status,
            result.executed_qty,
            result.avg_price,
        )
        return result

    @staticmethod
    def _generate_client_order_id() -> str:
        """Generate deterministic-like unique client order ID for retries."""
        millis = int(time.time() * 1000)
        suffix = uuid.uuid4().hex[:8]
        return f"tb_{millis}_{suffix}"
