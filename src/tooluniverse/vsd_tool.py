from __future__ import annotations

from typing import Any, Dict

from .tool_registry import register_tool
from .vsd_registry import load_catalog, save_catalog, upsert_tool
from .dynamic_rest_runner import refresh_generated_registry, remove_generated_tool
from .vsd_utils import build_config, probe_config, stamp_metadata


class VerifiedSourceRegisterTool:
    name = "VerifiedSourceRegisterTool"
    description = "Register a DynamicREST tool in the verified-source directory"
    input_schema = {
        "type": "object",
        "properties": {
            "tool_name": {"type": "string"},
            "tool_type": {"type": "string", "default": "dynamic_rest"},
            "candidate": {"type": "object"},
            "default_params": {"type": "object"},
            "default_headers": {"type": "object"},
            "force": {"type": "boolean", "default": False},
        },
        "required": ["tool_name", "candidate"],
    }

    def __call__(
        self,
        tool_name: str,
        candidate: Dict[str, Any],
        tool_type: str = "dynamic_rest",
        default_params: Dict[str, Any] | None = None,
        default_headers: Dict[str, Any] | None = None,
        force: bool = False,
    ) -> Dict[str, Any]:
        if not tool_name:
            raise ValueError("tool_name is required")

        cfg = build_config(
            candidate or {},
            tool_type=tool_type,
            default_params=default_params,
            default_headers=default_headers,
        )

        probe = probe_config(cfg)
        stamp_metadata(cfg, probe)

        if not probe.get("ok") and not force:
            return {
                "registered": False,
                "name": tool_name,
                "error": "Endpoint validation failed",
                "test": probe,
                "suggestion": "Provide default_params/default_headers or retry with force=True after ensuring credentials.",
            }

        cfg = upsert_tool(tool_name, cfg)
        refresh_generated_registry()

        return {"registered": True, "name": tool_name, "config": cfg}

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self.__call__(
            tool_name=arguments.get("tool_name"),
            candidate=arguments.get("candidate", {}),
            tool_type=arguments.get("tool_type", "dynamic_rest"),
            default_params=arguments.get("default_params"),
            default_headers=arguments.get("default_headers"),
            force=bool(arguments.get("force")),
        )


class VerifiedSourceDiscoveryTool:
    name = "VerifiedSourceDiscoveryTool"
    description = "Return the Verified-Source catalog."

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        catalog = load_catalog()
        return {"ok": True, "tools": list(catalog.values())}


class VerifiedSourceRemoveTool:
    name = "VerifiedSourceRemoveTool"
    description = "Remove a generated tool from the Verified-Source catalog."
    input_schema = {
        "type": "object",
        "properties": {
            "tool_name": {"type": "string"},
        },
        "required": ["tool_name"],
    }

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool_name = arguments.get("tool_name")
        if not tool_name:
            return {"removed": False, "error": "tool_name is required"}
        catalog = load_catalog()
        if tool_name not in catalog:
            return {"removed": False, "error": f"Unknown tool '{tool_name}'"}
        del catalog[tool_name]
        save_catalog(catalog)
        remove_generated_tool(tool_name)
        return {"removed": True, "name": tool_name}


def register(server):
    register_tool(VerifiedSourceRegisterTool.name, VerifiedSourceRegisterTool)
    register_tool(VerifiedSourceDiscoveryTool.name, VerifiedSourceDiscoveryTool)
    register_tool(VerifiedSourceRemoveTool.name, VerifiedSourceRemoveTool)

    server.add_tool(VerifiedSourceRegisterTool.name, VerifiedSourceRegisterTool())
    server.add_tool(VerifiedSourceDiscoveryTool.name, VerifiedSourceDiscoveryTool())
    server.add_tool(VerifiedSourceRemoveTool.name, VerifiedSourceRemoveTool())
    refresh_generated_registry()
