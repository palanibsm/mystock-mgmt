from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

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
        provider = os.getenv("AI_PROVIDER", "openai")
        return cls(
            provider=provider,
            tier=os.getenv("AI_TIER", "economy"),
            api_key=os.getenv("AI_API_KEY", ""),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            max_monthly_budget_usd=float(os.getenv("AI_MONTHLY_BUDGET", "5.0")),
            insights_on_load=os.getenv("AI_INSIGHTS_ON_LOAD", "true").lower() == "true",
            monitor_interval_seconds=int(os.getenv("AI_MONITOR_INTERVAL", "300")),
            price_alert_threshold_pct=float(os.getenv("AI_PRICE_ALERT_PCT", "5.0")),
        )

    @property
    def is_configured(self) -> bool:
        if self.provider == "ollama":
            return True
        return bool(self.api_key)
