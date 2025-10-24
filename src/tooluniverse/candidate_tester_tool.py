from __future__ import annotations

from typing import Any, Dict

from .tool_registry import register_tool
from .vsd_utils import build_config, probe_config


@register_tool("HarvestCandidateTesterTool")
class HarvestCandidateTesterTool:
    """
    Validate harvest/VSD candidates without registering them.
    Returns HTTP diagnostics and suggestions for default params or headers.
    """

    name = "HarvestCandidateTesterTool"
    description = "Test a harvest candidate endpoint to see if it returns usable JSON."
    input_schema = {
        "type": "object",
        "properties": {
            "candidate": {"type": "object"},
            "tool_type": {"type": "string", "default": "dynamic_rest"},
            "default_params": {"type": "object"},
            "default_headers": {"type": "object"},
        },
        "required": ["candidate"],
        "additionalProperties": False,
    }

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        candidate = arguments.get("candidate") or {}
        tool_type = arguments.get("tool_type") or "dynamic_rest"
        default_params = arguments.get("default_params")
        default_headers = arguments.get("default_headers")

        cfg = build_config(
            candidate,
            tool_type=tool_type,
            default_params=default_params,
            default_headers=default_headers,
        )
        probe = probe_config(cfg)

        return {
            "ok": bool(probe.get("ok")),
            "test": probe,
            "config": cfg,
        }
