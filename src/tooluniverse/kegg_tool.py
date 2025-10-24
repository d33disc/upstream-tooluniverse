from typing import List

import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

KEGG_BASE_URL = "https://rest.kegg.jp"
REQUEST_TIMEOUT = 30


@register_tool("KEGGTool")
class KEGGTool(BaseTool):
    """
    Lightweight wrapper around the KEGG REST API for text-based queries.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def run(self, arguments):
        query = (arguments or {}).get("query")
        if not query:
            return {"error": "Missing required parameter: query"}

        database = (arguments or {}).get("database") or self.tool_config.get(
            "database", "pathway"
        )
        max_results = (arguments or {}).get("max_results") or self.tool_config.get(
            "max_results"
        )

        endpoint = f"{KEGG_BASE_URL}/find/{database}/{query}"
        response = self.session.get(endpoint, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()

        lines: List[str] = [
            line for line in response.text.splitlines() if line.strip()
        ]
        if max_results:
            try:
                limit = int(max_results)
                lines = lines[: max(limit, 0)]
            except ValueError:
                pass

        results = []
        for line in lines:
            if "\t" in line:
                identifier, description = line.split("\t", 1)
            else:
                identifier, description = line, ""
            results.append({"id": identifier, "description": description})

        return results
