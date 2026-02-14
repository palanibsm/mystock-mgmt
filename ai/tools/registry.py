from __future__ import annotations

import json
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Callable] = {}
        self._schemas: dict[str, dict] = {}

    def register(self, func: Callable, description: str, parameters: dict) -> None:
        name = func.__name__
        self._tools[name] = func
        self._schemas[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }

    def get_schemas(self) -> list[dict]:
        return list(self._schemas.values())

    def execute(self, function_name: str, arguments: dict[str, Any]) -> str:
        func = self._tools.get(function_name)
        if not func:
            return json.dumps({"error": f"Unknown tool: {function_name}"})
        try:
            result = func(**arguments)
            return json.dumps(result, default=str)
        except Exception as e:
            logger.warning("Tool %s failed: %s", function_name, e)
            return json.dumps({"error": str(e)})
