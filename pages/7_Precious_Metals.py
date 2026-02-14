import streamlit as st
from components.holding_form import render_add_form, render_holdings_list
from utils.constants import Category

st.header("Precious Metals (OCBC)")
st.caption("Manage your Gold and Silver holdings from OCBC Singapore. Prices in SGD per gram.")

render_add_form(Category.PRECIOUS_METAL, broker_default="OCBC")
st.divider()
render_holdings_list(Category.PRECIOUS_METAL)
