from __future__ import annotations

import logging

import yfinance as yf

from db.database import get_cached_price, upsert_price_cache
from db.models import PriceData
from services.forex_data import get_exchange_rate
from utils.constants import TROY_OZ_TO_GRAMS

logger = logging.getLogger(__name__)

METAL_TICKERS = {
    "GOLD": "GC=F",
    "SILVER": "SI=F",
}

METALS_TTL_MINUTES = 15


def get_metal_price_sgd_per_gram(metal: str) -> PriceData | None:
    """Get metal price in SGD per gram (matching OCBC buy units)."""
    cache_key = f"METAL_{metal}_SGD"
    cached = get_cached_price(cache_key, METALS_TTL_MINUTES)
    if cached and cached.get("current_price"):
        return PriceData(
            current_price=cached["current_price"],
            all_time_high=cached.get("all_time_high", 0),
            all_time_low=cached.get("all_time_low", 0),
            trend=cached.get("trend", "SIDEWAYS"),
        )

    ticker_symbol = METAL_TICKERS.get(metal.upper())
    if not ticker_symbol:
        return None

    try:
        ticker = yf.Ticker(ticker_symbol)

        # Current price in USD per troy ounce
        hist_1d = ticker.history(period="5d")
        if hist_1d.empty:
            return None
        price_usd_oz = float(hist_1d["Close"].iloc[-1])

        # Convert: USD/troy oz -> USD/gram -> SGD/gram
        usd_sgd = get_exchange_rate("USD", "SGD")
        if not usd_sgd:
            usd_sgd = 1.35  # fallback
        price_sgd_gram = (price_usd_oz / TROY_OZ_TO_GRAMS) * usd_sgd

        # ATH/ATL
        hist_max = ticker.history(period="max")
        if not hist_max.empty:
            ath_usd_oz = float(hist_max["High"].max())
            atl_usd_oz = float(hist_max["Low"].min())
            ath_sgd = (ath_usd_oz / TROY_OZ_TO_GRAMS) * usd_sgd
            atl_sgd = (atl_usd_oz / TROY_OZ_TO_GRAMS) * usd_sgd
        else:
            ath_sgd = price_sgd_gram
            atl_sgd = price_sgd_gram

        # Trend
        hist_3m = ticker.history(period="3mo")
        if hist_3m is not None and len(hist_3m) >= 20:
            close = hist_3m["Close"]
            sma5 = close.rolling(5).mean().iloc[-1]
            sma20 = close.rolling(20).mean().iloc[-1]
            if sma5 > sma20 * 1.01:
                trend = "UP"
            elif sma5 < sma20 * 0.99:
                trend = "DOWN"
            else:
                trend = "SIDEWAYS"
        else:
            trend = "SIDEWAYS"

        price_data = PriceData(
            current_price=round(price_sgd_gram, 2),
            all_time_high=round(ath_sgd, 2),
            all_time_low=round(atl_sgd, 2),
            trend=trend,
        )

        upsert_price_cache(cache_key, {
            "current_price": price_data.current_price,
            "all_time_high": price_data.all_time_high,
            "all_time_low": price_data.all_time_low,
            "trend": trend,
            "currency": "SGD",
        })

        return price_data

    except Exception as e:
        logger.warning("Failed to fetch metal price for %s: %s", metal, e)
        return None
