import os
from typing import Any, Dict, List

import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

IUCN_BASE_URL = "https://apiv3.iucnredlist.org/api/v3/species/"
IUCN_TOKEN_ENV = "IUCN_RED_LIST_TOKEN"
REQUEST_TIMEOUT = 30


@register_tool("IUCNRedListTool")
class IUCNRedListTool(BaseTool):
    """
    Wrapper around the IUCN Red List API for species status lookups.
    Requires an API token supplied via arguments, tool config, or environment.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def _resolve_token(self, arguments: Dict[str, Any]) -> str:
        candidate = (
            (arguments or {}).get("token")
            or self.tool_config.get("token")
            or os.getenv(IUCN_TOKEN_ENV)
        )
        if not candidate:
            raise ValueError(
                f"Missing IUCN API token. Provide 'token' argument or set {IUCN_TOKEN_ENV}."
            )
        return candidate

    def run(self, arguments):
        species = (arguments or {}).get("species") or (arguments or {}).get(
            "species_name"
        )
        if not species:
            return {"error": "Missing required parameter: species"}

        try:
            token = self._resolve_token(arguments or {})
        except ValueError as exc:
            return {"error": str(exc)}

        response = self.session.get(
            f"{IUCN_BASE_URL}{species}",
            params={"token": token},
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code == 404:
            return {"count": 0, "results": []}

        response.raise_for_status()
        payload = response.json()

        results: List[Dict[str, Any]] = []
        for entry in payload.get("result", []):
            results.append(
                {
                    "scientific_name": entry.get("scientific_name"),
                    "category": entry.get("category"),
                    "population_trend": entry.get("population_trend"),
                    "distribution": entry.get("countries"),
                    "published_year": entry.get("published_year"),
                }
            )

        return {"count": len(results), "results": results}
