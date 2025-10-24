
from __future__ import annotations
import requests
from typing import Any, Dict
from .base_tool import BaseTool
from .tool_registry import register_tool
from .vsd_registry import load_catalog

@register_tool("RestRequestTool")
class RestRequestTool(BaseTool):
    name = "RestRequestTool"
    key = "rest-request-tool"
    description = "Execute a request defined in the Verified-Source catalog by tool_name."
    tool_type = "normal"
    enabled = True
    visible = True

    def __init__(self, tool_config=None):
        super().__init__(tool_config or {})

    def run(self, arguments: dict):
        tool_name = arguments.get("tool_name")
        params = arguments.get("params") or {}
        method = (arguments.get("method") or "GET").upper()
        if not tool_name:
            return {"ok": False, "error": "tool_name is required"}
        catalog = load_catalog()
        meta = catalog.get(tool_name)
        if not meta:
            return {"ok": False, "error": f"Unknown tool '{tool_name}' in catalog."}
        url = meta.get("endpoint")
        if not url:
            return {"ok": False, "error": f"Catalog entry for '{tool_name}' missing 'endpoint'."}
        merged_params = {}
        if isinstance(meta.get("default_params"), dict):
            merged_params.update(meta["default_params"])
        if isinstance(params, dict):
            merged_params.update(params)
        http_method = (method or meta.get("method") or "GET").upper()
        headers = {}
        if isinstance(meta.get("default_headers"), dict):
            headers.update(meta["default_headers"])
        headers.setdefault("Accept", "application/json")
        try:
            if http_method == "GET":
                r = requests.get(url, params=merged_params, headers=headers, timeout=60)
            else:
                r = requests.request(http_method, url, json=merged_params, headers=headers, timeout=60)
        except Exception as e:
            return {"ok": False, "error": f"HTTP error: {e!r}"}
        try:
            body = r.json()
        except Exception:
            body = {"status": r.status_code, "text": r.text}
        return {"ok": True, "status": r.status_code, "data": body}

def register(server):
    inst = RestRequestTool({})
    def _call(**kwargs): return inst.run(kwargs)
    server.add_tool(RestRequestTool.name, _call, RestRequestTool.description, {"key": RestRequestTool.key, "tool_type":"normal", "enabled": True, "visible": True})
