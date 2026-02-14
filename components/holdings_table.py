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

    # Group holdings by symbol
    grouped: dict[str, dict] = {}
    for e in enriched:
        sym_key = e.holding.symbol or ""
        if sym_key not in grouped:
            grouped[sym_key] = {
                "name": e.holding.name or "",
                "symbol": sym_key,
                "total_qty": 0.0,
                "total_invested": 0.0,
                "current_price": e.current_price if e.current_price is not None else 0,
                "trend": e.trend,
                "ath": e.all_time_high if e.all_time_high else 0,
                "atl": e.all_time_low if e.all_time_low else 0,
            }
        qty = e.holding.quantity if e.holding.quantity is not None else 0
        grouped[sym_key]["total_qty"] += qty
        grouped[sym_key]["total_invested"] += e.total_invested if e.total_invested is not None else 0

    rows = []
    for g in grouped.values():
        total_qty = g["total_qty"]
        total_invested = g["total_invested"]
        avg_buy_price = (total_invested / total_qty) if total_qty else 0
        current_value = total_qty * g["current_price"]
        pnl = current_value - total_invested
        pnl_pct = (pnl / total_invested * 100) if total_invested else 0

        rows.append({
            "Name": g["name"],
            "Symbol": g["symbol"],
            "Qty": total_qty,
            "Avg Buy": avg_buy_price,
            "Current": g["current_price"],
            "Invested": total_invested,
            "Value": current_value,
            "P&L": pnl,
            "P&L %": pnl_pct,
            "Trend": trend_arrow(g["trend"]) if g["trend"] else "—",
            "ATH": g["ath"],
            "ATL": g["atl"],
        })

    df = pd.DataFrame(rows)

    col_config = {
        "Name": st.column_config.TextColumn("Name", width="medium"),
        "Symbol": st.column_config.TextColumn("Symbol", width="small"),
        "Qty": st.column_config.NumberColumn("Qty", format="%.3f"),
        "Avg Buy": st.column_config.NumberColumn(f"Avg Buy ({sym})", format="%.3f"),
        "Current": st.column_config.NumberColumn(f"Current ({sym})", format="%.3f"),
        "Invested": st.column_config.NumberColumn(f"Invested ({sym})", format="%.3f"),
        "Value": st.column_config.NumberColumn(f"Value ({sym})", format="%.3f"),
        "P&L": st.column_config.NumberColumn(f"P&L ({sym})", format="%.3f"),
        "P&L %": st.column_config.NumberColumn("P&L %", format="%.1f%%"),
        "Trend": st.column_config.TextColumn("Trend", width="small"),
        "ATH": st.column_config.NumberColumn(f"ATH ({sym})", format="%.3f"),
        "ATL": st.column_config.NumberColumn(f"ATL ({sym})", format="%.3f"),
    }

    st.dataframe(df, column_config=col_config, use_container_width=True, hide_index=True)
