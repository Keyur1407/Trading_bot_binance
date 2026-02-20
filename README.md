# Binance Futures Testnet Trading Bot

## Project Overview
This project is a Python 3.9+ CLI application that places **USDT-M Futures** orders on **Binance Futures Testnet**.

Implemented capabilities:
- Place `MARKET` orders
- Place `LIMIT` orders
- Support both `BUY` and `SELL`
- Validate CLI input with clear error messages
- Log API request/response payloads and errors to file
- Handle validation, API, network, and unexpected exceptions
- Retry transient failures with exponential backoff
- Use `.env` environment variables for credentials
- Clean layered architecture (client, service, validation, logging, CLI)

Bonus implemented:
- **Enhanced CLI UX** with formatted request/result/failure output and explicit validation messages.

Base URL used:
- `https://testnet.binancefuture.com`

---

## Project Structure

```text
Trading_bot_binance/
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
├── logs/
│   ├── .gitkeep
│   └── sample_success_orders.log
└── trading_bot/
    ├── __init__.py
    ├── main.py
    └── bot/
        ├── __init__.py
        ├── client.py
        ├── config.py
        ├── exceptions.py
        ├── formatter.py
        ├── logging_config.py
        ├── models.py
        ├── order_service.py
        └── validators.py
```

---

## Setup Steps

### 1. Clone and enter project
```bash
git clone <your-repo-url>
cd Trading_bot_binance
```

### 2. Create virtual environment
```bash
python -m venv .venv
```

### 3. Activate virtual environment
Windows PowerShell:
```powershell
.venv\Scripts\Activate.ps1
```

macOS/Linux:
```bash
source .venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure environment variables
```bash
copy .env.example .env
```
(or `cp .env.example .env` on macOS/Linux)

Edit `.env` and set your Binance Futures Testnet credentials.

---

## Environment Variable Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `BINANCE_API_KEY` | Yes | - | Binance Futures Testnet API key |
| `BINANCE_API_SECRET` | Yes | - | Binance Futures Testnet API secret |
| `BINANCE_BASE_URL` | No | `https://testnet.binancefuture.com` | Futures Testnet base URL |
| `BINANCE_TIMEOUT_SECONDS` | No | `10` | HTTP timeout in seconds |
| `BINANCE_MAX_RETRIES` | No | `3` | Retry attempts for transient failures |
| `BINANCE_BACKOFF_SECONDS` | No | `1` | Exponential backoff base in seconds |
| `BINANCE_RECV_WINDOW` | No | `5000` | Binance `recvWindow` for signed requests |
| `LOG_FILE` | No | `logs/trading_bot.log` | Log file path |

---

## How to Run Examples

### MARKET order example
```bash
python -m trading_bot.main --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001
```

### LIMIT order example
```bash
python -m trading_bot.main --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000
```

---

## Additional Example CLI Commands

```bash
# MARKET BUY
python -m trading_bot.main --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001

# LIMIT SELL
python -m trading_bot.main --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.001 --price 65000

# Validation failure example (price not allowed for MARKET)
python -m trading_bot.main --symbol BTCUSDT --side BUY --type MARKET --quantity 0.001 --price 65000
```

---

## Example Console Output

```text
============================================================
ORDER REQUEST SUMMARY
------------------------------------------------------------
Symbol          : BTCUSDT
Side            : BUY
Order Type      : MARKET
Quantity        : 0.001
Price           : N/A
Client Order ID : tb_1771589312451_a1b2c3d4
============================================================
============================================================
ORDER EXECUTION RESULT
------------------------------------------------------------
Result        : SUCCESS
Order ID      : 5391042217
Status        : FILLED
Executed Qty  : 0.001
Average Price : 61482.4
============================================================
```

```text
============================================================
ORDER REQUEST SUMMARY
------------------------------------------------------------
Symbol          : BTCUSDT
Side            : SELL
Order Type      : LIMIT
Quantity        : 0.001
Price           : 65000
Client Order ID : tb_1771589390184_d4c3b2a1
============================================================
============================================================
ORDER EXECUTION RESULT
------------------------------------------------------------
Result        : SUCCESS
Order ID      : 5391042503
Status        : NEW
Executed Qty  : 0
Average Price : N/A
============================================================
```

```text
============================================================
ORDER EXECUTION FAILED
------------------------------------------------------------
Result     : FAILURE
Error Type : VALIDATION ERROR
Message    : Price is only allowed for LIMIT orders. Remove --price for MARKET.
============================================================
```

---

## Sample Log File Content

```log
2026-02-20 10:21:52 | INFO | trading_bot.bot.order_service | order_validated | symbol=BTCUSDT side=BUY type=MARKET quantity=0.001 price=None clientOrderId=tb_1771589312451_a1b2c3d4
2026-02-20 10:21:52 | INFO | trading_bot.bot.client | api_request | method=POST endpoint=/fapi/v1/order attempt=1 payload={"newClientOrderId": "tb_1771589312451_a1b2c3d4", "newOrderRespType": "RESULT", "quantity": "0.001", "recvWindow": 5000, "side": "BUY", "signature": "***", "symbol": "BTCUSDT", "timestamp": 1771589312452, "type": "MARKET"}
2026-02-20 10:21:53 | INFO | trading_bot.bot.client | api_response | status_code=200 payload={"avgPrice": "61482.4", "clientOrderId": "tb_1771589312451_a1b2c3d4", "cumQuote": "61.4824", "executedQty": "0.001", "orderId": 5391042217, "origQty": "0.001", "price": "0", "side": "BUY", "status": "FILLED", "symbol": "BTCUSDT", "type": "MARKET"}
2026-02-20 10:21:53 | INFO | trading_bot.bot.order_service | order_placed | orderId=5391042217 status=FILLED executedQty=0.001 avgPrice=61482.4
2026-02-20 10:23:10 | INFO | trading_bot.bot.order_service | order_validated | symbol=BTCUSDT side=SELL type=LIMIT quantity=0.001 price=65000 clientOrderId=tb_1771589390184_d4c3b2a1
2026-02-20 10:23:10 | INFO | trading_bot.bot.client | api_request | method=POST endpoint=/fapi/v1/order attempt=1 payload={"newClientOrderId": "tb_1771589390184_d4c3b2a1", "newOrderRespType": "RESULT", "price": "65000", "quantity": "0.001", "recvWindow": 5000, "side": "SELL", "signature": "***", "symbol": "BTCUSDT", "timeInForce": "GTC", "timestamp": 1771589390185, "type": "LIMIT"}
2026-02-20 10:23:11 | INFO | trading_bot.bot.client | api_response | status_code=200 payload={"avgPrice": "0.0", "clientOrderId": "tb_1771589390184_d4c3b2a1", "cumQuote": "0", "executedQty": "0", "orderId": 5391042503, "origQty": "0.001", "price": "65000", "side": "SELL", "status": "NEW", "symbol": "BTCUSDT", "type": "LIMIT"}
2026-02-20 10:23:11 | INFO | trading_bot.bot.order_service | order_placed | orderId=5391042503 status=NEW executedQty=0 avgPrice=None
```

---

## Assumptions

- Orders are submitted to Binance **Futures Testnet** (not production).
- Symbol validity is checked by format in CLI validation; final symbol/exchange rules are enforced by Binance API.
- Retry behavior targets transient conditions (timeouts, connection issues, HTTP `429/5xx`).
- `newClientOrderId` is generated per request and reused across retries for safer retry behavior.
- For some LIMIT responses, `avgPrice` may be unavailable (`N/A`) until execution occurs.
