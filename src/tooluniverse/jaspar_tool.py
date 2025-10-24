import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

JASPAR_BASE_URL = "https://jaspar.elixir.no/api/v1/matrix/"
REQUEST_TIMEOUT = 30


@register_tool("JASPARRestTool")
class JASPARRestTool(BaseTool):
    """
    Wrapper around the JASPAR REST API for matrix searches.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def run(self, arguments):
        query = (arguments or {}).get("query") or (arguments or {}).get("search")
        if not query:
            return {"error": "Missing required parameter: query"}

        params = {
            "search": query,
            "page": (arguments or {}).get("page", 1),
            "page_size": (arguments or {}).get("page_size")
            or self.tool_config.get("page_size", 10),
        }

        for optional in ("tax_group", "collection", "type"):
            value = (arguments or {}).get(optional)
            if value:
                params[optional] = value

        response = self.session.get(
            JASPAR_BASE_URL, params=params, timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()
        payload = response.json()

        results = []
        for item in payload.get("results", []):
            results.append(
                {
                    "matrix_id": item.get("matrix_id"),
                    "name": item.get("name"),
                    "collection": item.get("collection"),
                    "tax_group": item.get("tax_group"),
                    "class": item.get("class"),
                    "family": item.get("family"),
                }
            )

        return {
            "count": payload.get("count", len(results)),
            "next": payload.get("next"),
            "previous": payload.get("previous"),
            "results": results,
        }
