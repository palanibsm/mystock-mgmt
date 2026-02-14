import streamlit as st
from components.holding_form import render_add_form, render_holdings_list
from utils.constants import Category

st.header("Indian Stocks (NSE/BSE)")
st.caption("Manage your Indian stock holdings. Use Yahoo Finance symbols: e.g. RELIANCE.NS, TCS.NS, INFY.BO")

render_add_form(Category.INDIAN_STOCK, broker_default="Zerodha")
st.divider()
render_holdings_list(Category.INDIAN_STOCK)
