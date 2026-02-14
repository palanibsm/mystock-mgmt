from __future__ import annotations

import streamlit as st

from ai.config import AIConfig
from ai.agents.insights_agent import InsightsAgent, InsightsReport

SEVERITY_ICONS = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
}

CATEGORY_LABELS = {
    "diversification": "Diversification",
    "performance": "Performance",
    "risk": "Risk",
    "opportunity": "Opportunity",
    "alert": "Alert",
}


def render_insights_panel() -> None:
    config = AIConfig.from_env()
    if not config.is_configured:
        st.caption("AI insights unavailable — configure AI_API_KEY in .env")
        return

    st.subheader("AI Portfolio Insights")

    col1, col2 = st.columns([3, 1])
    with col2:
        regenerate = st.button("Generate Insights", type="primary")

    if "insights_report" not in st.session_state or regenerate:
        if not regenerate and not config.insights_on_load:
            st.caption("Click 'Generate Insights' to analyze your portfolio.")
            return

        with st.spinner("AI is analyzing your portfolio..."):
            try:
                agent = InsightsAgent(config)
                report = agent.generate()
                st.session_state.insights_report = report
            except Exception as e:
                st.error(f"Failed to generate insights: {e}")
                return

    report: InsightsReport = st.session_state.insights_report

    with col1:
        st.caption(f"{report.summary} | Model: {report.model_used} | Cost: ${report.cost_usd:.4f}")

    for insight in report.insights:
        icon = SEVERITY_ICONS.get(insight.severity, "ℹ️")
        category = CATEGORY_LABELS.get(insight.category, insight.category)
        expanded = insight.severity == "critical"

        with st.expander(f"{icon} [{category}] {insight.title}", expanded=expanded):
            st.markdown(insight.description)
            if insight.affected_holdings:
                st.caption(f"Affected: {', '.join(insight.affected_holdings)}")
