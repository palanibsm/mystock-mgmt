import streamlit as st
from components.holding_form import render_add_form, render_holdings_list
from utils.constants import Category

st.header("US Stocks (NYSE/NASDAQ)")
st.caption("Manage your US stock holdings. Use ticker symbols: e.g. AAPL, MSFT, GOOGL, AMZN")

render_add_form(Category.US_STOCK, broker_default="Tiger Trade")
st.divider()
render_holdings_list(Category.US_STOCK)
