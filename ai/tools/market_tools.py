from __future__ import annotations

import logging

import requests
import yfinance as yf

from ai.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def register_market_tools(registry: ToolRegistry) -> None:

    def get_current_price(symbol: str) -> dict:
        """Fetch current market price for a stock/ETF."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="5d")
            if hist.empty:
                return {"symbol": symbol, "error": "No data available"}
            current = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else current
            change_pct = (current - prev_close) / prev_close * 100
            return {
                "symbol": symbol,
                "current_price": round(current, 2),
                "previous_close": round(prev_close, 2),
                "day_change_pct": round(change_pct, 2),
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    registry.register(
        func=get_current_price,
        description="Fetch the current market price for a stock or ETF using its Yahoo Finance ticker symbol (e.g. RELIANCE.NS, D05.SI, AAPL).",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Yahoo Finance ticker symbol."},
            },
            "required": ["symbol"],
        },
    )

    def get_mutual_fund_nav(scheme_code: str) -> dict:
        """Fetch latest NAV for an Indian mutual fund."""
        try:
            resp = requests.get(f"https://api.mfapi.in/mf/{scheme_code}/latest", timeout=10)
            resp.raise_for_status()
            data = resp.json()
            nav_data = data.get("data", [{}])[0] if data.get("data") else {}
            return {
                "scheme_code": scheme_code,
                "scheme_name": data.get("meta", {}).get("scheme_name"),
                "nav": nav_data.get("nav"),
                "date": nav_data.get("date"),
            }
        except Exception as e:
            return {"scheme_code": scheme_code, "error": str(e)}

    registry.register(
        func=get_mutual_fund_nav,
        description="Fetch the latest NAV for an Indian mutual fund using its AMFI scheme code.",
        parameters={
            "type": "object",
            "properties": {
                "scheme_code": {"type": "string", "description": "AMFI scheme code (e.g. '119597')."},
            },
            "required": ["scheme_code"],
        },
    )

    def get_forex_rate(from_currency: str, to_currency: str) -> dict:
        """Get current exchange rate between two currencies."""
        try:
            resp = requests.get(
                "https://api.frankfurter.dev/latest",
                params={"from": from_currency, "to": to_currency},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()
            rate = data["rates"][to_currency]
            return {"from": from_currency, "to": to_currency, "rate": rate}
        except Exception as e:
            return {"from": from_currency, "to": to_currency, "error": str(e)}

    registry.register(
        func=get_forex_rate,
        description="Get the current exchange rate between two currencies (e.g. USD to SGD, INR to SGD).",
        parameters={
            "type": "object",
            "properties": {
                "from_currency": {"type": "string", "description": "Source currency code (e.g. USD, SGD, INR)."},
                "to_currency": {"type": "string", "description": "Target currency code."},
            },
            "required": ["from_currency", "to_currency"],
        },
    )

    def get_52_week_range(symbol: str) -> dict:
        """Get 52-week high/low for a stock."""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            if hist.empty:
                return {"symbol": symbol, "error": "No data"}
            current = float(hist["Close"].iloc[-1])
            high_52w = float(hist["High"].max())
            low_52w = float(hist["Low"].min())
            pct_below = (high_52w - current) / high_52w * 100
            return {
                "symbol": symbol,
                "current_price": round(current, 2),
                "52_week_high": round(high_52w, 2),
                "52_week_low": round(low_52w, 2),
                "pct_below_52w_high": round(pct_below, 2),
            }
        except Exception as e:
            return {"symbol": symbol, "error": str(e)}

    registry.register(
        func=get_52_week_range,
        description="Get the 52-week high/low prices for a stock and how far it is from its 52-week high.",
        parameters={
            "type": "object",
            "properties": {
                "symbol": {"type": "string", "description": "Yahoo Finance ticker symbol."},
            },
            "required": ["symbol"],
        },
    )
