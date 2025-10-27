"""
MedLog integration tools.

These tools expose MedLog collector and FHIR linkage capabilities as native
ToolUniverse tools for event ingestion, querying, and audit retrieval.
"""

from __future__ import annotations

import os
from typing import Any, Dict

import requests

from .base_tool import BaseTool
from .tool_registry import register_tool


class _MedLogBaseTool(BaseTool):
    """Shared utility methods for MedLog REST integration."""

    DEFAULT_BASE_URL = "http://localhost:7001"

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        self.base_url = os.getenv(
            "MEDLOG_COLLECTOR_BASE_URL", self.DEFAULT_BASE_URL
        ).rstrip("/")
        self.session = requests.Session()

    def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.post(url, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            return {"error": f"MedLog collector request failed: {exc}", "endpoint": url}

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.base_url}{path}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            return {"error": f"MedLog collector request failed: {exc}", "endpoint": url}


class _MedLogFHIRBaseTool(BaseTool):
    """Shared logic for interacting with the MedLog FHIR linkage service."""

    DEFAULT_FHIR_URL = "http://localhost:7003"

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        self.fhir_base = os.getenv(
            "MEDLOG_FHIR_BASE_URL", self.DEFAULT_FHIR_URL
        ).rstrip("/")
        self.session = requests.Session()

    def _get(self, path: str) -> Dict[str, Any]:
        url = f"{self.fhir_base}{path}"
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as exc:  # pragma: no cover - network errors
            return {"error": f"MedLog FHIR request failed: {exc}", "endpoint": url}


@register_tool("MedLogInitEventTool")
class MedLogInitEventTool(_MedLogBaseTool):
    """Create or update a MedLog event record."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/medlog/events/init", arguments)


@register_tool("MedLogAppendFragmentTool")
class MedLogAppendFragmentTool(_MedLogBaseTool):
    """Append fragment data (artifacts, outputs, feedback) to an event."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        event_id = arguments.get("event_id")
        fragment = arguments.get("fragment", {})
        if not event_id:
            return {"error": "Parameter 'event_id' is required."}
        return self._post(f"/medlog/events/{event_id}/append", fragment)


@register_tool("MedLogGetProvenanceTool")
class MedLogGetProvenanceTool(_MedLogBaseTool):
    """Retrieve PROV-JSON bundle for a specific event."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        event_id = arguments.get("event_id")
        if not event_id:
            return {"error": "Parameter 'event_id' is required."}
        return self._get(f"/medlog/events/{event_id}/prov")


@register_tool("MedLogQueryEventsTool")
class MedLogQueryEventsTool(_MedLogBaseTool):
    """Query MedLog events by run_id or event_id."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "run_id": arguments.get("run_id"),
            "event_id": arguments.get("event_id"),
            "limit": arguments.get("limit", 50),
        }
        return self._post("/query", payload)


@register_tool("MedLogExportParquetTool")
class MedLogExportParquetTool(_MedLogBaseTool):
    """Trigger a parquet export of MedLog events."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        return self._post("/export/parquet", {})


@register_tool("MedLogFHIRBundleTool")
class MedLogFHIRBundleTool(_MedLogFHIRBaseTool):
    """Fetch FHIR bundle for a specific event."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        event_id = arguments.get("event_id")
        if not event_id:
            return {"error": "Parameter 'event_id' is required."}
        return self._get(f"/bundle/{event_id}")


@register_tool("MedLogFHIRRunBundleTool")
class MedLogFHIRRunBundleTool(_MedLogFHIRBaseTool):
    """Fetch FHIR bundle aggregating all events in a run."""

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        run_id = arguments.get("run_id")
        if not run_id:
            return {"error": "Parameter 'run_id' is required."}
        return self._get(f"/bundle/run/{run_id}")
