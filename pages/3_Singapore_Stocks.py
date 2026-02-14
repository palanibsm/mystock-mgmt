import streamlit as st
from components.holding_form import render_add_form, render_holdings_list
from utils.constants import Category

st.header("Singapore Stocks (SGX)")
st.caption("Manage your Singapore stock holdings. Use Yahoo Finance symbols: e.g. D05.SI (DBS), O39.SI (OCBC), U11.SI (UOB)")

render_add_form(Category.SG_STOCK, broker_default="Tiger Trade")
st.divider()
render_holdings_list(Category.SG_STOCK)
