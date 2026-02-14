from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

import litellm

from ai.config import AIConfig

logger = logging.getLogger(__name__)

# Suppress litellm verbose logging
litellm.suppress_debug_info = True


@dataclass
class ToolCall:
    id: str
    function_name: str
    arguments: dict[str, Any]


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)
    model: str = ""
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0


class LLMProvider:
    def __init__(self, config: AIConfig):
        self._config = config
        self._set_api_keys()

    def _set_api_keys(self) -> None:
        provider = self._config.provider
        key = self._config.api_key
        if provider == "openai":
            os.environ["OPENAI_API_KEY"] = key
        elif provider == "anthropic":
            os.environ["ANTHROPIC_API_KEY"] = key
        elif provider == "gemini":
            os.environ["GEMINI_API_KEY"] = key
        if provider == "ollama":
            os.environ["OLLAMA_API_BASE"] = self._config.ollama_base_url

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str = "auto",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        model_id = self._config.model_id

        kwargs: dict[str, Any] = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice

        try:
            raw = litellm.completion(**kwargs)
            return self._normalize(raw)
        except Exception as e:
            logger.error("LLM call failed: %s", e)
            raise

    def _normalize(self, raw: Any) -> LLMResponse:
        choice = raw.choices[0]
        message = choice.message

        tool_calls = []
        if message.tool_calls:
            for tc in message.tool_calls:
                tool_calls.append(ToolCall(
                    id=tc.id,
                    function_name=tc.function.name,
                    arguments=json.loads(tc.function.arguments),
                ))

        cost = 0.0
        try:
            cost = litellm.completion_cost(raw)
        except Exception:
            pass

        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            model=raw.model,
            input_tokens=raw.usage.prompt_tokens if raw.usage else 0,
            output_tokens=raw.usage.completion_tokens if raw.usage else 0,
            cost_usd=cost,
        )
