import os
from typing import Any, Dict, List

import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

CBIOPORTAL_BASE_URL = "https://www.cbioportal.org/api"
CBIOPORTAL_TOKEN_ENV = "CBIOPORTAL_API_TOKEN"
REQUEST_TIMEOUT = 30


@register_tool("CBioPortalTool")
class CBioPortalTool(BaseTool):
    """
    Wrapper around the cBioPortal REST API for study discovery.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def _headers(self, arguments: Dict[str, Any]) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        token = (
            arguments.get("token")
            or self.tool_config.get("token")
            or os.getenv(CBIOPORTAL_TOKEN_ENV)
        )
        if token:
            headers["X-Auth-Token"] = token
        return headers

    def run(self, arguments):
        keyword = (arguments or {}).get("keyword") or (arguments or {}).get("query")
        if not keyword:
            return {"error": "Missing required parameter: keyword"}

        page_size = int(
            (arguments or {}).get("page_size")
            or self.tool_config.get("page_size", 20)
        )
        page_number = int((arguments or {}).get("page") or 0)

        params = {
            "keyword": keyword,
            "pageSize": max(page_size, 1),
            "pageNumber": max(page_number, 0),
            "projection": "SUMMARY",
        }

        response = self.session.get(
            f"{CBIOPORTAL_BASE_URL}/studies",
            params=params,
            headers=self._headers(arguments or {}),
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        results: List[Dict[str, Any]] = []
        for item in payload:
            results.append(
                {
                    "studyId": item.get("studyId"),
                    "name": item.get("name"),
                    "description": item.get("description"),
                    "cancerTypeId": item.get("cancerTypeId"),
                    "publicStudy": item.get("publicStudy"),
                }
            )

        return {"results": results, "returned": len(results)}
