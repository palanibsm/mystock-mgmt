from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from ai.config import AIConfig
from ai.llm_provider import LLMProvider
from ai.tools.registry import ToolRegistry
from ai.prompts.system_prompts import CHAT_SYSTEM_PROMPT

logger = logging.getLogger(__name__)

MAX_TOOL_ROUNDS = 5


@dataclass
class ChatSession:
    messages: list[dict] = field(default_factory=list)
    total_cost_usd: float = 0.0
    total_input_tokens: int = 0
    total_output_tokens: int = 0

    def add_user_message(self, content: str) -> None:
        self.messages.append({"role": "user", "content": content})

    def add_assistant_message(self, content: str) -> None:
        self.messages.append({"role": "assistant", "content": content})

    def add_tool_result(self, tool_call_id: str, content: str) -> None:
        self.messages.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "content": content,
        })


class ChatAgent:
    def __init__(self, config: AIConfig, registry: ToolRegistry):
        self._provider = LLMProvider(config)
        self._registry = registry
        self._config = config

    def respond(self, session: ChatSession, user_message: str) -> str:
        session.add_user_message(user_message)

        # Ensure system prompt
        if not session.messages or session.messages[0].get("role") != "system":
            session.messages.insert(0, {"role": "system", "content": CHAT_SYSTEM_PROMPT})

        tool_schemas = self._registry.get_schemas()

        for _ in range(MAX_TOOL_ROUNDS):
            response = self._provider.chat(
                messages=session.messages,
                tools=tool_schemas,
                tool_choice="auto",
            )
            session.total_cost_usd += response.cost_usd
            session.total_input_tokens += response.input_tokens
            session.total_output_tokens += response.output_tokens

            # No tool calls — final answer
            if not response.tool_calls:
                answer = response.content or "I could not generate a response."
                session.add_assistant_message(answer)
                return answer

            # Tool calls — execute and feed back
            assistant_msg = {
                "role": "assistant",
                "content": response.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function_name,
                            "arguments": json.dumps(tc.arguments),
                        },
                    }
                    for tc in response.tool_calls
                ],
            }
            session.messages.append(assistant_msg)

            for tc in response.tool_calls:
                logger.info("Tool call: %s(%s)", tc.function_name, tc.arguments)
                result = self._registry.execute(tc.function_name, tc.arguments)
                session.add_tool_result(tc.id, result)

        return "I reached the maximum number of tool-use rounds. Please try a simpler question."
