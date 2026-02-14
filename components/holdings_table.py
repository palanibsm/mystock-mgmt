from __future__ import annotations

import streamlit as st
import pandas as pd

from db.models import EnrichedHolding
from utils.constants import CURRENCY_SYMBOLS, CATEGORY_LABELS
from components.trend_indicator import trend_arrow


def render_holdings_table(
    enriched: list[EnrichedHolding],
    category: str,
    currency: str,
) -> None:
    if not enriched:
        return

    sym = CURRENCY_SYMBOLS.get(currency, currency)
    label = CATEGORY_LABELS.get(category, category)

    st.subheader(label)

    rows = []
    for e in enriched:
        rows.append({
            "Name": e.holding.name,
            "Symbol": e.holding.symbol,
            "Qty": e.holding.quantity,
            f"Buy Price ({sym})": e.holding.buy_price,
            f"Current ({sym})": e.current_price,
            f"P&L ({sym})": e.pnl,
            "P&L %": e.pnl_pct,
            "Trend": trend_arrow(e.trend),
            f"ATH ({sym})": e.all_time_high,
            f"ATL ({sym})": e.all_time_low,
        })

    df = pd.DataFrame(rows)

    # Style P&L columns
    def color_pnl(val):
        if isinstance(val, (int, float)):
            color = "green" if val >= 0 else "red"
            return f"color: {color}"
        return ""

    pnl_col = f"P&L ({sym})"
    styled = df.style.applymap(color_pnl, subset=[pnl_col, "P&L %"])
    styled = styled.format({
        "Qty": "{:.4g}",
        f"Buy Price ({sym})": "{:,.2f}",
        f"Current ({sym})": "{:,.2f}",
        pnl_col: "{:+,.2f}",
        "P&L %": "{:+.1f}%",
        f"ATH ({sym})": "{:,.2f}",
        f"ATL ({sym})": "{:,.2f}",
    })

    st.dataframe(styled, use_container_width=True, hide_index=True)
