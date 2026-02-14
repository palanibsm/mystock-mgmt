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
        pnl = e.pnl if e.pnl is not None else 0.0
        pnl_pct = e.pnl_pct if e.pnl_pct is not None else 0.0
        rows.append({
            "Name": e.holding.name or "",
            "Symbol": e.holding.symbol or "",
            "Qty": e.holding.quantity if e.holding.quantity is not None else 0,
            "Buy Price": e.holding.buy_price if e.holding.buy_price is not None else 0,
            "Current": e.current_price if e.current_price is not None else 0,
            "P&L": pnl,
            "P&L %": pnl_pct,
            "Trend": trend_arrow(e.trend) if e.trend else "—",
            "ATH": e.all_time_high if e.all_time_high else 0,
            "ATL": e.all_time_low if e.all_time_low else 0,
        })

    df = pd.DataFrame(rows)

    col_config = {
        "Name": st.column_config.TextColumn("Name", width="medium"),
        "Symbol": st.column_config.TextColumn("Symbol", width="small"),
        "Qty": st.column_config.NumberColumn("Qty", format="%.4g"),
        "Buy Price": st.column_config.NumberColumn(f"Buy ({sym})", format="%.2f"),
        "Current": st.column_config.NumberColumn(f"Current ({sym})", format="%.2f"),
        "P&L": st.column_config.NumberColumn(f"P&L ({sym})", format="%.2f"),
        "P&L %": st.column_config.NumberColumn("P&L %", format="%.1f%%"),
        "Trend": st.column_config.TextColumn("Trend", width="small"),
        "ATH": st.column_config.NumberColumn(f"ATH ({sym})", format="%.2f"),
        "ATL": st.column_config.NumberColumn(f"ATL ({sym})", format="%.2f"),
    }

    st.dataframe(df, column_config=col_config, use_container_width=True, hide_index=True)
