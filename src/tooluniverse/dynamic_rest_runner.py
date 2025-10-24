from __future__ import annotations

"""
DynamicRESTRunner (fastmcp-agnostic)
Executes HTTP requests for tools described in data/generated_tools.json.
"""

import json
import os
from typing import Any, Dict, Iterable
import requests
from .common_utils import vsd_generated_path

_REGISTRY: dict[str, dict[str, Any]] = {}
_LOADED: bool = False

def _registry_path() -> str:
    return vsd_generated_path()

def _load_generated_registry() -> None:
    global _REGISTRY, _LOADED
    if _LOADED:
        return
    path = _registry_path()
    if not os.path.isfile(path):
        _LOADED = True
        return

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def _ingest(name: str, cfg: Dict[str, Any]) -> None:
        entry = dict(cfg)
        entry.setdefault("name", name)
        _REGISTRY[name] = entry

    if isinstance(data, dict):
        generated = data.get("generated_tools")
        if isinstance(generated, Iterable):
            for item in generated:
                if isinstance(item, dict) and item.get("name"):
                    _ingest(item["name"], item)
        else:
            for name, cfg in data.items():
                if isinstance(cfg, dict):
                    _ingest(name, cfg)

    _LOADED = True


def refresh_generated_registry() -> None:
    """Force a reload from disk."""
    global _LOADED
    _REGISTRY.clear()
    _LOADED = False
    _load_generated_registry()


def upsert_generated_tool(tool_name: str, cfg: Dict[str, Any]) -> None:
    """Update the in-process cache with a new generated tool."""
    _REGISTRY[tool_name] = dict(cfg, name=tool_name)
    global _LOADED
    _LOADED = True


def remove_generated_tool(tool_name: str) -> None:
    _REGISTRY.pop(tool_name, None)

def _run_dynamic(tool_name: str, params: dict | None = None, method: str | None = None) -> dict:
    _load_generated_registry()
    meta = _REGISTRY.get(tool_name)
    if not meta:
        # attempt a forced reload in case a different process updated the file
        refresh_generated_registry()
        meta = _REGISTRY.get(tool_name)
    if not meta:
        raise ValueError(f"Unknown generated tool: {tool_name}. Add it to {_registry_path()}")

    url = meta.get("endpoint")
    if not url:
        base_url = meta.get("base_url")
        routes = meta.get("routes") or []
        if base_url and routes:
            first = routes[0]
            path = first.get("path") or "/"
            url = (base_url.rstrip("/") + path) if path.startswith("/") else f"{base_url.rstrip('/')}/{path}"
            meta.setdefault("method", first.get("method", "GET"))
        elif base_url:
            url = base_url
        else:
            raise ValueError(f"Catalog entry '{tool_name}' is missing an endpoint.")

    http_method = (method or meta.get("method") or "GET").upper()
    params = {**(meta.get("default_params") or {}), **(params or {})}
    if http_method == "GET":
        r = requests.get(url, params=params, timeout=60)
    else:
        r = requests.request(http_method, url, json=params, timeout=60)
    r.raise_for_status()
    try:
        return r.json()
    except Exception:
        return {"status": r.status_code, "text": r.text}

def register(server) -> None:
    def dynamic_rest_runner(tool_name: str, params: dict | None = None, method: str | None = None) -> dict:
        return _run_dynamic(tool_name, params, method)

    dynamic_rest_runner.name = "DynamicRESTRunner"
    dynamic_rest_runner.description = "Run an HTTP request for a generated tool name from data/generated_tools.json"
    dynamic_rest_runner.key = "dynamicrestrunner"
    dynamic_rest_runner.tool_type = "dynamic"
    dynamic_rest_runner.enabled = True
    dynamic_rest_runner.visible = True

    server.add_tool(dynamic_rest_runner)
