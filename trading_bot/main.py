"""CLI entry point for placing Binance Futures Testnet orders."""
from __future__ import annotations

import argparse
import os
import sys

from dotenv import load_dotenv

from .bot.client import BinanceFuturesClient
from .bot.config import Settings
from .bot.exceptions import APIError, ConfigurationError, NetworkError, ValidationError
from .bot.formatter import format_failure, format_order_request_summary, format_order_response
from .bot.logging_config import setup_logging
from .bot.models import OrderInput
from .bot.order_service import OrderService
from .bot.validators import validate_order_input


def build_parser() -> argparse.ArgumentParser:
    """Build CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="Place MARKET and LIMIT orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python -m trading_bot.main --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001\n"
            "  python -m trading_bot.main --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000"
        ),
    )
    parser.add_argument("--symbol", required=True, help="Trading pair symbol, e.g., BTCUSDT")
    parser.add_argument("--side", required=True, help="Order side: BUY or SELL")
    parser.add_argument("--type", dest="order_type", required=True, help="Order type: MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity (must be > 0)")
    parser.add_argument("--price", help="Price (required for LIMIT orders)")
    return parser


def main() -> int:
    """Run CLI workflow."""
    load_dotenv()
    bootstrap_log_file = os.getenv("LOG_FILE", "logs/trading_bot.log")
    logger = setup_logging(bootstrap_log_file)

    parser = build_parser()
    args = parser.parse_args()

    try:
        order_input = OrderInput(
            symbol=args.symbol,
            side=args.side,
            order_type=args.order_type,
            quantity=args.quantity,
            price=args.price,
        )
        validate_order_input(order_input)

        settings = Settings.from_env()
        logger = setup_logging(settings.log_file)

        client = BinanceFuturesClient(settings=settings, logger=logger.getChild("bot.client"))
        service = OrderService(client=client, logger=logger.getChild("bot.order_service"))

        order_request = service.create_order_request(order_input)
        print(format_order_request_summary(order_request))

        order_result = service.place_order(order_request)
        print(format_order_response(order_result))
        return 0

    except ValidationError as exc:
        logger.error("validation_error | message=%s", str(exc))
        print(format_failure("VALIDATION ERROR", str(exc)))
        return 2

    except ConfigurationError as exc:
        logger.error("configuration_error | message=%s", str(exc))
        print(format_failure("CONFIGURATION ERROR", str(exc)))
        return 3

    except APIError as exc:
        logger.error(
            "api_error | status_code=%s error_code=%s message=%s",
            exc.status_code,
            exc.error_code,
            exc.message,
        )
        print(format_failure("API ERROR", str(exc)))
        return 4

    except NetworkError as exc:
        logger.error("network_error | attempts=%s message=%s", exc.attempts, str(exc))
        print(format_failure("NETWORK ERROR", str(exc)))
        return 5

    except Exception as exc:  # pylint: disable=broad-except
        logger.exception("unexpected_exception | type=%s message=%s", type(exc).__name__, str(exc))
        print(format_failure("UNEXPECTED ERROR", "An unexpected error occurred. Check logs for details."))
        return 1


if __name__ == "__main__":
    sys.exit(main())
