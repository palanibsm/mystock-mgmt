from __future__ import annotations

import streamlit as st

from ai.agents.monitor_agent import AlertStore

SEVERITY_COLORS = {
    "critical": "red",
    "warning": "orange",
    "info": "blue",
}


def render_alert_sidebar(alert_store: AlertStore) -> None:
    alerts = alert_store.get_active()

    if not alerts:
        st.sidebar.caption("No active alerts")
        return

    st.sidebar.subheader(f"Alerts ({len(alerts)})")

    for i, alert in enumerate(alerts[:10]):  # Show max 10
        color = SEVERITY_COLORS.get(alert.severity, "gray")
        st.sidebar.markdown(
            f":{color}[**{alert.title}**]  \n"
            f"{alert.description}  \n"
            f"*{alert.timestamp.strftime('%H:%M')}*"
        )
        if st.sidebar.button("Dismiss", key=f"dismiss_{i}_{alert.timestamp.timestamp()}"):
            alert_store.dismiss(i)
            st.rerun()

    if st.sidebar.button("Clear All Alerts"):
        alert_store.clear_all()
        st.rerun()
