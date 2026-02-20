"""HTTP client for Binance Futures Testnet."""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import time
from typing import Any, Dict
from urllib.parse import urlencode

import requests

from .config import Settings
from .exceptions import APIError, NetworkError

TRANSIENT_STATUS_CODES = {429, 500, 502, 503, 504}


class BinanceFuturesClient:
    """Binance Futures REST client with retry and signed request support."""

    def __init__(self, settings: Settings, logger: logging.Logger) -> None:
        self._settings = settings
        self._logger = logger
        self._session = requests.Session()
        self._session.headers.update({"X-MBX-APIKEY": settings.api_key})

    def place_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Place MARKET or LIMIT order on Binance Futures Testnet."""
        return self._request(
            method="POST",
            endpoint="/fapi/v1/order",
            params=payload,
            signed=True,
        )

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any],
        signed: bool,
    ) -> Dict[str, Any]:
        base_params = dict(params)

        for attempt in range(1, self._settings.max_retries + 1):
            request_params = self._build_signed_params(base_params) if signed else dict(base_params)
            safe_payload = self._sanitize_for_log(request_params)

            self._logger.info(
                "api_request | method=%s endpoint=%s attempt=%s payload=%s",
                method,
                endpoint,
                attempt,
                json.dumps(safe_payload, sort_keys=True),
            )

            try:
                response = self._session.request(
                    method=method,
                    url=f"{self._settings.base_url}{endpoint}",
                    params=request_params,
                    timeout=self._settings.timeout_seconds,
                )
            except (requests.Timeout, requests.ConnectionError) as exc:
                self._logger.error(
                    "network_failure | endpoint=%s attempt=%s error=%s",
                    endpoint,
                    attempt,
                    str(exc),
                )
                if attempt == self._settings.max_retries:
                    raise NetworkError(
                        f"Network request failed after {attempt} attempts: {exc}",
                        attempts=attempt,
                    ) from exc
                self._sleep_before_retry(attempt)
                continue
            except requests.RequestException as exc:
                self._logger.error("requests_exception | endpoint=%s error=%s", endpoint, str(exc))
                raise NetworkError(f"Unexpected request failure: {exc}", attempts=attempt) from exc

            payload = self._parse_response_payload(response)

            if response.ok:
                self._logger.info(
                    "api_response | status_code=%s payload=%s",
                    response.status_code,
                    json.dumps(payload, sort_keys=True),
                )
                return payload

            self._logger.error(
                "api_error_response | status_code=%s payload=%s",
                response.status_code,
                json.dumps(payload, sort_keys=True),
            )

            if response.status_code in TRANSIENT_STATUS_CODES and attempt < self._settings.max_retries:
                self._sleep_before_retry(attempt)
                continue

            error_code = payload.get("code")
            message = str(payload.get("msg", "Binance API request failed."))
            raise APIError(
                status_code=response.status_code,
                error_code=error_code,
                message=message,
                response_payload=payload,
            )

        raise NetworkError("Unreachable retry branch.", attempts=self._settings.max_retries)

    def _build_signed_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        signed_params = dict(params)
        signed_params["timestamp"] = int(time.time() * 1000)
        signed_params["recvWindow"] = self._settings.recv_window

        query_string = urlencode(signed_params, doseq=True)
        signature = hmac.new(
            self._settings.api_secret.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        signed_params["signature"] = signature
        return signed_params

    @staticmethod
    def _parse_response_payload(response: requests.Response) -> Dict[str, Any]:
        try:
            data = response.json()
            if isinstance(data, dict):
                return data
            return {"raw": data}
        except ValueError:
            return {"raw": response.text}

    @staticmethod
    def _sanitize_for_log(params: Dict[str, Any]) -> Dict[str, Any]:
        safe = dict(params)
        if "signature" in safe:
            safe["signature"] = "***"
        return safe

    def _sleep_before_retry(self, attempt: int) -> None:
        delay_seconds = self._settings.backoff_seconds * (2 ** (attempt - 1))
        self._logger.warning("retry_wait | seconds=%.2f", delay_seconds)
        time.sleep(delay_seconds)
