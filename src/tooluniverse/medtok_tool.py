"""
MedTok integration tools.

These tools provide a thin wrapper around the MedTok FastAPI service so that
ToolUniverse users can tokenize, embed, and explore medical codes directly
from the unified tool catalog.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import requests

from .base_tool import BaseTool
from .tool_registry import register_tool


class _MedTokBaseTool(BaseTool):
    """Shared utilities for MedTok REST integrations."""

    DEFAULT_BASE_URL = "http://localhost:8000"

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        self.base_url = os.getenv("MEDTOK_BASE_URL", self.DEFAULT_BASE_URL).rstrip("/")
        self.session = requests.Session()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            return {"error": f"MedTok request failed: {exc}", "endpoint": url}

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            return {"error": f"MedTok request failed: {exc}", "endpoint": url}


@register_tool("MedTokTokenizeTool")
class MedTokTokenizeTool(_MedTokBaseTool):
    """Tokenize medical codes using MedTok multimodal tokenizer."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "codes": arguments.get("codes", []),
            "system": arguments.get("system", "ICD-10"),
            "include_metadata": arguments.get("include_metadata", False),
        }
        return self._post("/tokenize", payload)


@register_tool("MedTokEmbedTool")
class MedTokEmbedTool(_MedTokBaseTool):
    """Generate token embeddings for a batch of codes."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "codes": arguments.get("codes", []),
            "system": arguments.get("system", "ICD-10"),
        }
        return self._post("/embed", payload)


@register_tool("MedTokNearestNeighborsTool")
class MedTokNearestNeighborsTool(_MedTokBaseTool):
    """Retrieve nearest neighbours for a code in embedding space."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "code": arguments.get("code"),
            "k": arguments.get("k", 5),
            "system": arguments.get("system", "ICD-10"),
        }
        return self._post("/nearest_neighbors", payload)


@register_tool("MedTokMapTextTool")
class MedTokMapTextTool(_MedTokBaseTool):
    """Map free-text description to the closest medical code."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "text": arguments.get("text", ""),
            "system": arguments.get("system", "ICD-10"),
        }
        return self._post("/map_text_to_code", payload)


@register_tool("MedTokSearchTextTool")
class MedTokSearchTextTool(_MedTokBaseTool):
    """Perform text and semantic search across the code vocabulary."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "text": arguments.get("text", ""),
            "system": arguments.get("system"),
            "k": arguments.get("k", 5),
        }
        return self._post("/search_text", payload)


@register_tool("MedTokCodeInfoTool")
class MedTokCodeInfoTool(_MedTokBaseTool):
    """Fetch detailed metadata for a specific code."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        system = arguments.get("system", "ICD-10")
        code = arguments.get("code")
        if not code:
            return {"error": "Parameter 'code' is required."}
        path = f"/codes/{system}/{code}"
        return self._get(path)
