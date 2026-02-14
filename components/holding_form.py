from __future__ import annotations

import streamlit as st
from datetime import date

from db.database import add_holding, update_holding, delete_holding, get_holdings
from utils.constants import Category, CATEGORY_CURRENCIES, EXCHANGE_SUFFIXES


def _symbol_help(category: str) -> str:
    hints = {
        Category.INDIAN_STOCK: "Use Yahoo Finance format: RELIANCE.NS (NSE) or RELIANCE.BO (BSE)",
        Category.SG_STOCK: "Use Yahoo Finance format: D05.SI (DBS), O39.SI (OCBC)",
        Category.US_STOCK: "Use ticker symbol: AAPL, MSFT, GOOGL",
        Category.INDIAN_MF: "Use AMFI scheme code (e.g. 119551). Find at mfapi.in",
        Category.SG_MF: "Enter fund name as identifier",
        Category.PRECIOUS_METAL: "Use GOLD or SILVER",
    }
    return hints.get(category, "")


def render_add_form(category: str, broker_default: str = "") -> None:
    currency = CATEGORY_CURRENCIES.get(category, "SGD")

    with st.form(f"add_{category}", clear_on_submit=True):
        st.subheader("Add New Holding")
        cols = st.columns(2)

        with cols[0]:
            name = st.text_input("Name *", placeholder="e.g. Reliance Industries")
            if category == Category.PRECIOUS_METAL:
                symbol = st.selectbox("Metal *", ["GOLD", "SILVER"])
            else:
                symbol = st.text_input("Symbol *", help=_symbol_help(category))
            quantity = st.number_input("Quantity *", min_value=0.0001, step=1.0, format="%.4f")

        with cols[1]:
            buy_price = st.number_input(f"Buy Price ({currency}) *", min_value=0.01, step=0.01, format="%.2f")
            buy_date = st.date_input("Buy Date", value=date.today())
            broker = st.text_input("Broker", value=broker_default)

        notes = st.text_area("Notes", max_chars=500)
        submitted = st.form_submit_button("Add Holding", type="primary", use_container_width=True)

        if submitted:
            if not name or not symbol:
                st.error("Name and Symbol are required.")
                return
            add_holding({
                "category": category,
                "name": name.strip(),
                "symbol": symbol.strip().upper(),
                "quantity": quantity,
                "buy_price": buy_price,
                "buy_date": buy_date.isoformat() if buy_date else None,
                "currency": currency,
                "broker": broker.strip() if broker else None,
                "notes": notes.strip() if notes else None,
            })
            st.success(f"Added {name}!")
            st.rerun()


def render_holdings_list(category: str) -> None:
    holdings = get_holdings(category)
    if not holdings:
        st.info("No holdings yet. Add one above.")
        return

    currency = CATEGORY_CURRENCIES.get(category, "SGD")
    st.subheader(f"Your Holdings ({len(holdings)})")

    for h in holdings:
        total = h["quantity"] * h["buy_price"]
        with st.expander(f"**{h['name']}** ({h['symbol']}) — {h['quantity']:.4g} @ {currency} {h['buy_price']:,.2f} = {currency} {total:,.2f}"):
            edit_cols = st.columns(2)
            with edit_cols[0]:
                new_name = st.text_input("Name", value=h["name"], key=f"name_{h['id']}")
                new_symbol = st.text_input("Symbol", value=h["symbol"], key=f"sym_{h['id']}")
                new_qty = st.number_input("Quantity", value=float(h["quantity"]),
                                          min_value=0.0001, step=1.0, format="%.4f", key=f"qty_{h['id']}")
            with edit_cols[1]:
                new_price = st.number_input(f"Buy Price ({currency})", value=float(h["buy_price"]),
                                            min_value=0.01, step=0.01, format="%.2f", key=f"price_{h['id']}")
                new_date = st.text_input("Buy Date", value=h["buy_date"] or "", key=f"date_{h['id']}")
                new_broker = st.text_input("Broker", value=h["broker"] or "", key=f"broker_{h['id']}")

            new_notes = st.text_input("Notes", value=h["notes"] or "", key=f"notes_{h['id']}")

            btn_cols = st.columns(2)
            with btn_cols[0]:
                if st.button("Update", key=f"update_{h['id']}", type="primary", use_container_width=True):
                    update_holding(h["id"], {
                        "name": new_name.strip(),
                        "symbol": new_symbol.strip().upper(),
                        "quantity": new_qty,
                        "buy_price": new_price,
                        "buy_date": new_date.strip() if new_date else None,
                        "currency": currency,
                        "broker": new_broker.strip() if new_broker else None,
                        "notes": new_notes.strip() if new_notes else None,
                    })
                    st.success("Updated!")
                    st.rerun()
            with btn_cols[1]:
                if st.button("Delete", key=f"delete_{h['id']}", type="secondary", use_container_width=True):
                    delete_holding(h["id"])
                    st.warning(f"Deleted {h['name']}")
                    st.rerun()
