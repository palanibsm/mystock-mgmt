import streamlit as st
from components.holding_form import render_add_form, render_holdings_list
from db.database import get_holdings, upsert_price_cache, get_cached_price
from utils.constants import Category

st.header("Singapore Mutual Funds (Tiger Trade)")
st.caption("Manage your Singapore mutual fund holdings. Update current NAV manually from your Tiger Trade app.")

render_add_form(Category.SG_MF, broker_default="Tiger Trade")
st.divider()

# Manual NAV update section
holdings = get_holdings(Category.SG_MF)
if holdings:
    st.subheader("Update Current NAV")
    st.caption("Enter the latest NAV from Tiger Trade to see live P&L on the dashboard.")

    for h in holdings:
        cached = get_cached_price(h["symbol"], ttl_minutes=999999)
        current_nav = cached["current_price"] if cached and cached.get("current_price") else h["buy_price"]

        cols = st.columns([3, 2, 1])
        with cols[0]:
            st.text(f"{h['name']}")
        with cols[1]:
            new_nav = st.number_input(
                "Current NAV",
                value=float(current_nav),
                min_value=0.01,
                step=0.01,
                format="%.4f",
                key=f"nav_{h['id']}",
                label_visibility="collapsed",
            )
        with cols[2]:
            if st.button("Save", key=f"save_nav_{h['id']}", type="primary"):
                upsert_price_cache(h["symbol"], {
                    "current_price": new_nav,
                    "all_time_high": None,
                    "all_time_low": None,
                    "trend": "SIDEWAYS",
                    "currency": "SGD",
                })
                st.success(f"NAV updated to {new_nav:.4f}")
                st.rerun()

    st.divider()

render_holdings_list(Category.SG_MF)
