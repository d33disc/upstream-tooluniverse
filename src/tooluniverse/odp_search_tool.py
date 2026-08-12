"""USPTO ODP JSON-body POST search tool.

The ODP (Open Data Portal) API exposes two search families:

  1. GET query-param search  -- handled by USPTOOpenDataPortalTool
  2. POST JSON-body search   -- handled HERE by ODPSearchTool

ODP POST search endpoints (patent/applications/search, patent/status-codes,
petition/decisions/search, trials/*/search, appeals/decisions/search,
interferences/decisions/search) take an application/json body with a Lucene
query string (e.g. {"q": "applicationNumberText:14412875"}), unlike the DSAPI
endpoints which are form-encoded. Response envelopes differ per endpoint but
all are JSON and passed through unchanged.

Flow
----
    caller
      |
      v
    run(arguments)
      |-- validate: query present?
      |-- map: query->q, offset, limit (optional)
      |-- POST JSON body to USPTO API
      v
    {status, data}
"""

import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base_tool import BaseTool
from .tool_registry import register_tool

_BASE_URL = "https://api.uspto.gov/api/v1"


@register_tool("ODPSearchTool")
class ODPSearchTool(BaseTool):
    """HTTP adapter for USPTO ODP JSON-body POST search endpoints."""

    def __init__(
        self,
        tool_config: dict,
        api_key: str | None = None,
        base_url: str = _BASE_URL,
    ) -> None:
        super().__init__(tool_config)
        self.base_url = base_url

        api_key = api_key or os.environ.get("USPTO_API_KEY")
        if not api_key:
            raise ValueError(
                "USPTO_API_KEY environment variable is required. "
                "Get one at https://data.uspto.gov/apis/getting-started"
            )

        self.headers = {"X-API-KEY": api_key, "Accept": "application/json"}
        self.session = requests.Session()
        retry = Retry(
            total=5,
            status_forcelist=[429, 500, 502, 503, 504],
            backoff_factor=5,
            raise_on_status=False,
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retry))

    def run(self, arguments: dict | None = None) -> dict:
        """Execute an ODP JSON-body POST search.

        Maps agent-friendly parameter names to the ODP JSON body:
          query  -> q   (Lucene query string)
          offset, limit passed through when provided.
        """
        arguments = arguments or {}

        query = arguments.get("query")
        if not query:
            return self.tool_error(
                "Missing required parameter 'query'.",
                suggestion="Provide a Lucene query, e.g. 'applicationNumberText:14412875'",
            )

        endpoint = self.tool_config.get("api_endpoint")
        if not endpoint:
            return self.tool_error("No api_endpoint in tool configuration.")

        # ODP POST search bodies accept ONLY {"q": ...} -- offset/limit are
        # GET query params, not POST body fields. Verified live 2026-08-12:
        # every ODP search endpoint (applications, status-codes, petition,
        # PTAB families) returns 400 when the body carries offset/limit.
        body = {"q": query}

        url = f"{self.base_url}/{endpoint}"
        try:
            response = self.session.post(
                url,
                headers=self.headers,
                json=body,
                timeout=30,
            )
            response.raise_for_status()
            result = response.json()
        except requests.exceptions.RequestException as exc:
            return self.tool_error(
                f"ODP search request failed: {exc}",
                error_type="ToolUnavailableError",
            )

        return {"status": "success", "data": result}
