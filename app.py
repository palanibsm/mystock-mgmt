import streamlit as st
import yaml
import streamlit_authenticator as stauth
from db.database import init_db
from ai.config import AIConfig
from ai.agents.monitor_agent import MonitorAgent, AlertStore
from components.alert_sidebar import render_alert_sidebar

st.set_page_config(
    page_title="MyStock Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Authentication ---
with open("auth_config.yaml") as f:
    auth_config = yaml.safe_load(f)

authenticator = stauth.Authenticate(
    auth_config["credentials"],
    auth_config["cookie"]["name"],
    auth_config["cookie"]["key"],
    auth_config["cookie"]["expiry_days"],
)

authenticator.login()

if st.session_state.get("authentication_status") is None:
    st.info("Please enter your username and password.")
    st.stop()
elif st.session_state.get("authentication_status") is False:
    st.error("Username or password is incorrect.")
    st.stop()

# --- Authenticated beyond this point ---
init_db()

# Initialize background monitor (once per app lifecycle)
if "alert_store" not in st.session_state:
    st.session_state.alert_store = AlertStore()

if "monitor_started" not in st.session_state:
    config = AIConfig.from_env()
    monitor = MonitorAgent(
        alert_store=st.session_state.alert_store,
        interval_seconds=config.monitor_interval_seconds,
        threshold_pct=config.price_alert_threshold_pct,
    )
    monitor.start()
    st.session_state.monitor_started = True

# Navigation
dashboard = st.Page("pages/1_Dashboard.py", title="Dashboard", icon="📊", default=True)
indian_stocks = st.Page("pages/2_Indian_Stocks.py", title="Indian Stocks", icon="🇮🇳")
sg_stocks = st.Page("pages/3_Singapore_Stocks.py", title="Singapore Stocks", icon="🇸🇬")
us_stocks = st.Page("pages/4_US_Stocks.py", title="US Stocks", icon="🇺🇸")
indian_mf = st.Page("pages/5_Indian_Mutual_Funds.py", title="Indian Mutual Funds", icon="📈")
sg_mf = st.Page("pages/6_SG_Mutual_Funds.py", title="SG Mutual Funds", icon="📈")
precious_metals = st.Page("pages/7_Precious_Metals.py", title="Precious Metals", icon="🥇")
ai_chat = st.Page("pages/8_AI_Chat.py", title="AI Chat", icon="🤖")

nav = st.navigation({
    "Portfolio": [dashboard],
    "Manage Holdings": [indian_stocks, sg_stocks, us_stocks, indian_mf, sg_mf, precious_metals],
    "AI Assistant": [ai_chat],
})

# Sidebar: user info + logout + alerts
with st.sidebar:
    st.write(f"Welcome, **{st.session_state.get('name', '')}**")
    authenticator.logout("Logout", "sidebar")
    st.markdown("---")
    render_alert_sidebar(st.session_state.alert_store)
    st.markdown("---")
    st.caption("MyStock Manager v0.1")

nav.run()
