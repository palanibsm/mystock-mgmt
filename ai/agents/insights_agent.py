from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from ai.config import AIConfig
from ai.llm_provider import LLMProvider
from ai.prompts.insight_templates import INSIGHTS_SYSTEM_PROMPT, INSIGHTS_USER_TEMPLATE
from db import database as db

logger = logging.getLogger(__name__)


@dataclass
class Insight:
    category: str
    severity: str
    title: str
    description: str
    affected_holdings: list[str] = field(default_factory=list)


@dataclass
class InsightsReport:
    insights: list[Insight]
    summary: str
    cost_usd: float
    model_used: str


class InsightsAgent:
    def __init__(self, config: AIConfig):
        self._provider = LLMProvider(config)
        self._config = config

    def generate(self) -> InsightsReport:
        portfolio_data = self._gather_data()

        user_message = INSIGHTS_USER_TEMPLATE.format(
            portfolio_json=json.dumps(portfolio_data, indent=2, default=str)
        )

        response = self._provider.chat(
            messages=[
                {"role": "system", "content": INSIGHTS_SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.4,
            max_tokens=3000,
        )

        # Log usage
        db.log_ai_usage(
            provider=self._config.provider,
            model=response.model,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            cost_usd=response.cost_usd,
            feature="insights",
        )

        insights = self._parse(response.content)
        return InsightsReport(
            insights=insights,
            summary=self._summarize(insights),
            cost_usd=response.cost_usd,
            model_used=response.model,
        )

    def _gather_data(self) -> dict:
        holdings = db.get_holdings()
        enriched = []
        for h in holdings:
            entry = {
                "name": h["name"],
                "symbol": h["symbol"],
                "category": h["category"],
                "quantity": h["quantity"],
                "buy_price": h["buy_price"],
                "currency": h["currency"],
                "invested": h["quantity"] * h["buy_price"],
            }
            cached = db.get_cached_price(h["symbol"], ttl_minutes=1440)
            if cached and cached.get("current_price"):
                entry["current_price"] = cached["current_price"]
                entry["current_value"] = h["quantity"] * cached["current_price"]
                entry["return_pct"] = round(
                    (cached["current_price"] - h["buy_price"]) / h["buy_price"] * 100, 2
                )
                entry["all_time_high"] = cached.get("all_time_high")
                entry["all_time_low"] = cached.get("all_time_low")
                entry["trend"] = cached.get("trend")
            enriched.append(entry)

        return {
            "holdings": enriched,
            "total_holdings": len(enriched),
        }

    def _parse(self, content: str | None) -> list[Insight]:
        if not content:
            return [Insight("performance", "info", "Analysis Unavailable", "Could not generate insights.", [])]

        try:
            json_str = content
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0]

            data = json.loads(json_str)
            return [
                Insight(
                    category=item.get("category", "info"),
                    severity=item.get("severity", "info"),
                    title=item.get("title", ""),
                    description=item.get("description", ""),
                    affected_holdings=item.get("affected_holdings", []),
                )
                for item in data.get("insights", [])
            ]
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning("Failed to parse insights JSON: %s", e)
            return [Insight("performance", "info", "Portfolio Analysis", content, [])]

    def _summarize(self, insights: list[Insight]) -> str:
        critical = sum(1 for i in insights if i.severity == "critical")
        warnings = sum(1 for i in insights if i.severity == "warning")
        if critical:
            return f"{critical} critical issue(s) and {warnings} warning(s) detected."
        elif warnings:
            return f"{warnings} warning(s) found. Portfolio generally healthy."
        return "Portfolio looks healthy. No critical issues detected."
