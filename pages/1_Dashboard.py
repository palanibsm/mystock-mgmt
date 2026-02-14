from __future__ import annotations

import streamlit as st
from datetime import datetime

from db.database import get_holdings
from db.models import EnrichedHolding, Holding, PriceData
from services.market_data import get_stock_price
from services.mf_data import get_mf_price_data
from services.metals_data import get_metal_price_sgd_per_gram
from services.forex_data import convert_to_sgd
from components.summary_cards import render_summary_cards
from components.holdings_table import render_holdings_table
from utils.constants import Category, CATEGORY_CURRENCIES, CATEGORY_LABELS

st.header("Portfolio Dashboard")
st.caption("Single pane of glass — all investments across India, Singapore, and USA")

# Refresh button
col1, col2 = st.columns([3, 1])
with col2:
    refresh = st.button("Refresh Prices", type="primary")

all_holdings = get_holdings()

if not all_holdings:
    st.info("No holdings yet. Use the sidebar to add your stocks, mutual funds, and precious metals.")
    st.stop()


def _get_price(holding: dict) -> PriceData | None:
    cat = holding["category"]
    symbol = holding["symbol"]

    if cat in (Category.INDIAN_STOCK, Category.SG_STOCK, Category.US_STOCK):
        return get_stock_price(symbol)
    elif cat == Category.INDIAN_MF:
        return get_mf_price_data(symbol)
    elif cat == Category.PRECIOUS_METAL:
        return get_metal_price_sgd_per_gram(symbol)
    elif cat == Category.SG_MF:
        return None
    return None


# Enrich holdings with live data
enriched_all: list[EnrichedHolding] = []
with st.spinner("Fetching live prices..."):
    for h in all_holdings:
        price_data = _get_price(h)

        if price_data:
            current_price = price_data.current_price
            ath = price_data.all_time_high
            atl = price_data.all_time_low
            trend = price_data.trend
        else:
            current_price = h["buy_price"]
            ath = 0
            atl = 0
            trend = "SIDEWAYS"

        total_invested = h["quantity"] * h["buy_price"]
        current_value = h["quantity"] * current_price
        pnl = current_value - total_invested
        pnl_pct = (pnl / total_invested * 100) if total_invested else 0

        currency = h["currency"]
        current_value_sgd = convert_to_sgd(current_value, currency)

        holding_obj = Holding(
            id=h["id"],
            category=h["category"],
            name=h["name"],
            symbol=h["symbol"],
            quantity=h["quantity"],
            buy_price=h["buy_price"],
            buy_date=h.get("buy_date"),
            currency=currency,
            broker=h.get("broker"),
            notes=h.get("notes"),
        )

        enriched_all.append(EnrichedHolding(
            holding=holding_obj,
            current_price=current_price,
            total_invested=total_invested,
            current_value=current_value,
            pnl=pnl,
            pnl_pct=pnl_pct,
            all_time_high=ath,
            all_time_low=atl,
            trend=trend,
            current_value_sgd=current_value_sgd,
        ))

# Build category totals
category_totals = {}
for e in enriched_all:
    cat = e.holding.category
    if cat not in category_totals:
        currency = CATEGORY_CURRENCIES.get(cat, "SGD")
        category_totals[cat] = {
            "current_value": 0,
            "total_invested": 0,
            "currency": currency,
            "count": 0,
        }
    category_totals[cat]["current_value"] += e.current_value
    category_totals[cat]["total_invested"] += e.total_invested
    category_totals[cat]["count"] += 1

# Render summary cards
render_summary_cards(enriched_all, category_totals)

st.markdown("---")

# Render per-category tables
for cat in Category:
    cat_enriched = [e for e in enriched_all if e.holding.category == cat]
    if cat_enriched:
        currency = CATEGORY_CURRENCIES.get(cat, "SGD")
        render_holdings_table(cat_enriched, cat, currency)

# AI Insights panel
st.markdown("---")
from components.ai_insights_panel import render_insights_panel
render_insights_panel()

# Footer
st.markdown("---")
st.caption(f"Last refreshed: {datetime.now().strftime('%d %b %Y, %I:%M %p')}")
