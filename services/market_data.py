from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import yfinance as yf

from db.database import get_cached_price, upsert_price_cache
from db.models import PriceData

logger = logging.getLogger(__name__)

PRICE_TTL_MINUTES = 15
ATH_TTL_MINUTES = 1440  # 24 hours


def _compute_trend(history) -> str:
    if history is None or len(history) < 20:
        return "SIDEWAYS"
    close = history["Close"]
    sma5 = close.rolling(5).mean().iloc[-1]
    sma20 = close.rolling(20).mean().iloc[-1]
    if sma5 > sma20 * 1.01:
        return "UP"
    elif sma5 < sma20 * 0.99:
        return "DOWN"
    return "SIDEWAYS"


def get_stock_price(symbol: str) -> PriceData | None:
    cached = get_cached_price(symbol, PRICE_TTL_MINUTES)
    if cached and cached.get("current_price"):
        return PriceData(
            current_price=cached["current_price"],
            all_time_high=cached.get("all_time_high", 0),
            all_time_low=cached.get("all_time_low", 0),
            trend=cached.get("trend", "SIDEWAYS"),
        )

    try:
        ticker = yf.Ticker(symbol)

        # Current price from recent history
        hist_1d = ticker.history(period="5d")
        if hist_1d.empty:
            return None
        current_price = float(hist_1d["Close"].iloc[-1])

        # ATH/ATL from max history
        ath_cached = get_cached_price(symbol, ATH_TTL_MINUTES)
        if ath_cached and ath_cached.get("all_time_high"):
            ath = ath_cached["all_time_high"]
            atl = ath_cached["all_time_low"]
        else:
            hist_max = ticker.history(period="max")
            if not hist_max.empty:
                ath = float(hist_max["High"].max())
                atl = float(hist_max["Low"].min())
            else:
                ath = current_price
                atl = current_price

        # Trend from 3-month history
        hist_3m = ticker.history(period="3mo")
        trend = _compute_trend(hist_3m)

        price_data = PriceData(
            current_price=current_price,
            all_time_high=ath,
            all_time_low=atl,
            trend=trend,
        )

        upsert_price_cache(symbol, {
            "current_price": current_price,
            "all_time_high": ath,
            "all_time_low": atl,
            "trend": trend,
            "currency": None,
        })

        return price_data

    except Exception as e:
        logger.warning("Failed to fetch price for %s: %s", symbol, e)
        return None


def batch_fetch_prices(symbols: list[str]) -> dict[str, PriceData | None]:
    results = {}
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {executor.submit(get_stock_price, s): s for s in symbols}
        for future in as_completed(futures):
            symbol = futures[future]
            try:
                results[symbol] = future.result()
            except Exception:
                results[symbol] = None
    return results
