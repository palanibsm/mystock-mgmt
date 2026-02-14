import streamlit as st
from components.holding_form import render_add_form, render_holdings_list
from utils.constants import Category

st.header("Singapore Mutual Funds (Tiger Trade)")
st.caption("Manage your Singapore mutual fund holdings. No live NAV API available — update current NAV manually.")

st.info("Singapore MF NAVs must be entered manually. Check your Tiger Trade app for current NAV values.")

render_add_form(Category.SG_MF, broker_default="Tiger Trade")
st.divider()
render_holdings_list(Category.SG_MF)
