import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

INTERPRO_BASE_URL = "https://www.ebi.ac.uk/interpro/api/entry/interpro/"
REQUEST_TIMEOUT = 30


@register_tool("InterProTool")
class InterProTool(BaseTool):
    """
    Tool wrapper for the InterPro REST API.
    Provides entry search with pagination support.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def run(self, arguments):
        query = (arguments or {}).get("query") or (arguments or {}).get("search")
        if not query:
            return {"error": "Missing required parameter: query"}

        page = int((arguments or {}).get("page") or 1)
        page_size = int(
            (arguments or {}).get("page_size")
            or self.tool_config.get("page_size", 25)
        )

        params = {
            "search": query,
            "page": max(page, 1),
            "page_size": max(min(page_size, 200), 1),
        }

        response = self.session.get(
            INTERPRO_BASE_URL, params=params, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        payload = response.json()

        entries = []
        for item in payload.get("results", []):
            metadata = item.get("metadata", {})
            entries.append(
                {
                    "accession": metadata.get("accession"),
                    "name": metadata.get("name"),
                    "short_name": metadata.get("short_name"),
                    "type": metadata.get("type"),
                    "source_database": metadata.get("source_database"),
                    "integrated": metadata.get("integrated"),
                }
            )

        return {
            "count": payload.get("count", len(entries)),
            "next": payload.get("next"),
            "previous": payload.get("previous"),
            "results": entries,
        }
