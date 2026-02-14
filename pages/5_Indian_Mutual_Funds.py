import streamlit as st
import requests
from components.holding_form import render_add_form, render_holdings_list
from utils.constants import Category

st.header("Indian Mutual Funds (Zerodha)")
st.caption("Manage your Indian mutual fund holdings. Use AMFI scheme codes from mfapi.in")

with st.expander("Search Mutual Fund Scheme Code"):
    query = st.text_input("Search by fund name", placeholder="e.g. Parag Parikh Flexi Cap")
    if query and len(query) >= 3:
        try:
            resp = requests.get(f"https://api.mfapi.in/mf/search?q={query}", timeout=10)
            if resp.status_code == 200:
                results = resp.json()
                if results:
                    for r in results[:10]:
                        st.code(f"{r['schemeCode']} — {r['schemeName']}")
                else:
                    st.warning("No results found.")
            else:
                st.error("Search API unavailable.")
        except Exception as e:
            st.error(f"Search failed: {e}")

render_add_form(Category.INDIAN_MF, broker_default="Zerodha")
st.divider()
render_holdings_list(Category.INDIAN_MF)
