from __future__ import annotations

import logging

import requests

from db.database import get_cached_price, upsert_price_cache
from db.models import PriceData

logger = logging.getLogger(__name__)

BASE_URL = "https://api.mfapi.in"
MF_TTL_MINUTES = 30


def search_mutual_funds(query: str) -> list[dict]:
    try:
        resp = requests.get(f"{BASE_URL}/mf/search", params={"q": query}, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("MF search failed: %s", e)
        return []


def get_mf_price_data(scheme_code: str) -> PriceData | None:
    cached = get_cached_price(scheme_code, MF_TTL_MINUTES)
    if cached and cached.get("current_price"):
        return PriceData(
            current_price=cached["current_price"],
            all_time_high=cached.get("all_time_high", 0),
            all_time_low=cached.get("all_time_low", 0),
            trend=cached.get("trend", "SIDEWAYS"),
        )

    try:
        resp = requests.get(f"{BASE_URL}/mf/{scheme_code}", timeout=15)
        resp.raise_for_status()
        data = resp.json()

        nav_history = data.get("data", [])
        if not nav_history:
            return None

        current_nav = float(nav_history[0]["nav"])
        all_navs = [float(d["nav"]) for d in nav_history]
        ath = max(all_navs)
        atl = min(all_navs)

        # Trend: compare current vs 30 days ago
        if len(all_navs) > 30:
            nav_30d = all_navs[30]
            pct_change = (current_nav - nav_30d) / nav_30d * 100
            if pct_change > 1:
                trend = "UP"
            elif pct_change < -1:
                trend = "DOWN"
            else:
                trend = "SIDEWAYS"
        else:
            trend = "SIDEWAYS"

        price_data = PriceData(
            current_price=current_nav,
            all_time_high=ath,
            all_time_low=atl,
            trend=trend,
        )

        upsert_price_cache(scheme_code, {
            "current_price": current_nav,
            "all_time_high": ath,
            "all_time_low": atl,
            "trend": trend,
            "currency": "INR",
        })

        return price_data

    except Exception as e:
        logger.warning("Failed to fetch MF data for %s: %s", scheme_code, e)
        return None
