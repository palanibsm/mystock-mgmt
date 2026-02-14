from __future__ import annotations

import logging

import requests

from db.database import get_cached_forex, upsert_forex_cache

logger = logging.getLogger(__name__)

FRANKFURTER_URL = "https://api.frankfurter.dev/latest"
FOREX_TTL_MINUTES = 60


def get_exchange_rate(from_currency: str, to_currency: str) -> float | None:
    if from_currency == to_currency:
        return 1.0

    pair = f"{from_currency}{to_currency}"
    cached = get_cached_forex(pair, FOREX_TTL_MINUTES)
    if cached:
        return cached

    # Primary: Frankfurter API
    try:
        resp = requests.get(
            FRANKFURTER_URL,
            params={"from": from_currency, "to": to_currency},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        rate = data["rates"][to_currency]
        upsert_forex_cache(pair, rate)
        return rate
    except Exception as e:
        logger.warning("Frankfurter API failed for %s->%s: %s", from_currency, to_currency, e)

    # Fallback: yfinance
    try:
        import yfinance as yf
        symbol = f"{from_currency}{to_currency}=X"
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if not hist.empty:
            rate = float(hist["Close"].iloc[-1])
            upsert_forex_cache(pair, rate)
            return rate
    except Exception as e:
        logger.warning("yfinance forex fallback failed for %s: %s", pair, e)

    return None


def convert_to_sgd(amount: float, from_currency: str) -> float:
    if from_currency == "SGD":
        return amount
    rate = get_exchange_rate(from_currency, "SGD")
    if rate:
        return amount * rate
    return amount  # fallback: return unconverted
