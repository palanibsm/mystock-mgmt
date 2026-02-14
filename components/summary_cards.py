from __future__ import annotations

import streamlit as st

from db.models import EnrichedHolding
from utils.constants import CATEGORY_LABELS, CURRENCY_SYMBOLS, Category
from utils.formatters import format_currency, format_percentage


def render_summary_cards(
    enriched: list[EnrichedHolding],
    category_totals: dict[str, dict],
) -> None:
    # Total portfolio in SGD
    total_value_sgd = sum(e.current_value_sgd for e in enriched)
    total_invested_sgd = sum(e.total_invested for e in enriched)  # rough — not converted, used for delta display

    st.metric(
        label="Total Portfolio Value (SGD)",
        value=format_currency(total_value_sgd, "SGD"),
    )

    st.markdown("---")

    # Category breakdown cards — 3 per row
    categories = list(CATEGORY_LABELS.keys())
    rows = [categories[i:i + 3] for i in range(0, len(categories), 3)]

    for row in rows:
        cols = st.columns(len(row))
        for col, cat in zip(cols, row):
            with col:
                info = category_totals.get(cat, {})
                value = info.get("current_value", 0)
                invested = info.get("total_invested", 0)
                currency = info.get("currency", "SGD")
                count = info.get("count", 0)
                pnl_pct = ((value - invested) / invested * 100) if invested else 0

                st.metric(
                    label=CATEGORY_LABELS[cat],
                    value=f"{CURRENCY_SYMBOLS.get(currency, currency)} {value:,.2f}",
                    delta=f"{format_percentage(pnl_pct)} ({count} holdings)",
                )
