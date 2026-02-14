from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_setting(key: str, default: str = "") -> str:
    """Read from env vars first, then fall back to st.secrets (Streamlit Cloud)."""
    val = os.getenv(key)
    if val:
        return val
    try:
        import streamlit as st
        return str(st.secrets.get(key, default))
    except Exception:
        return default

MODEL_CATALOG = {
    "openai": {
        "economy": "gpt-4o-mini",
        "quality": "gpt-4o",
    },
    "anthropic": {
        "economy": "claude-haiku-4-5-20251001",
        "quality": "claude-sonnet-4-5-20250929",
    },
    "gemini": {
        "economy": "gemini/gemini-2.0-flash",
        "quality": "gemini/gemini-2.5-pro",
    },
    "ollama": {
        "economy": "ollama/llama3.1:8b",
        "quality": "ollama/llama3.1:70b",
    },
}


@dataclass
class AIConfig:
    provider: str
    tier: str
    api_key: str
    ollama_base_url: str = "http://localhost:11434"
    max_monthly_budget_usd: float = 5.0
    insights_on_load: bool = True
    monitor_interval_seconds: int = 300
    price_alert_threshold_pct: float = 5.0

    @property
    def model_id(self) -> str:
        return MODEL_CATALOG[self.provider][self.tier]

    @classmethod
    def from_env(cls) -> AIConfig:
        provider = _get_setting("AI_PROVIDER", "openai")
        return cls(
            provider=provider,
            tier=_get_setting("AI_TIER", "economy"),
            api_key=_get_setting("AI_API_KEY", ""),
            ollama_base_url=_get_setting("OLLAMA_BASE_URL", "http://localhost:11434"),
            max_monthly_budget_usd=float(_get_setting("AI_MONTHLY_BUDGET", "5.0")),
            insights_on_load=_get_setting("AI_INSIGHTS_ON_LOAD", "true").lower() == "true",
            monitor_interval_seconds=int(_get_setting("AI_MONITOR_INTERVAL", "300")),
            price_alert_threshold_pct=float(_get_setting("AI_PRICE_ALERT_PCT", "5.0")),
        )

    @property
    def is_configured(self) -> bool:
        if self.provider == "ollama":
            return True
        return bool(self.api_key)
