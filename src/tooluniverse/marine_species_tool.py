from urllib.parse import quote

import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

WORMS_BASE_URL = "https://www.marinespecies.org/rest"
REQUEST_TIMEOUT = 30


@register_tool("MarineSpeciesTool")
class MarineSpeciesTool(BaseTool):
    """
    Wrapper for the World Register of Marine Species (WoRMS) REST API.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def run(self, arguments):
        name = (arguments or {}).get("scientific_name") or (arguments or {}).get(
            "name"
        )
        if not name:
            return {"error": "Missing required parameter: scientific_name"}

        like = (arguments or {}).get("like")
        marine_only = (arguments or {}).get("marine_only")

        params = {
            "like": "true"
            if (like if like is not None else self.tool_config.get("like", True))
            else "false",
            "marine_only": "true"
            if (
                marine_only
                if marine_only is not None
                else self.tool_config.get("marine_only", True)
            )
            else "false",
        }

        endpoint = f"{WORMS_BASE_URL}/AphiaRecordsByName/{quote(name)}"
        response = self.session.get(endpoint, params=params, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        payload = response.json() or []

        results = []
        for item in payload:
            results.append(
                {
                    "AphiaID": item.get("AphiaID"),
                    "scientificname": item.get("scientificname"),
                    "rank": item.get("rank"),
                    "status": item.get("status"),
                    "match_type": item.get("match_type"),
                }
            )

        return results
