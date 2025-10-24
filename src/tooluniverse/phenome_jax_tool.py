import requests

from .base_tool import BaseTool
from .tool_registry import register_tool

PHENOME_JAX_BASE_URL = "https://phenome.jax.org/api"
REQUEST_TIMEOUT = 30


@register_tool("PhenomeJaxTool")
class PhenomeJaxTool(BaseTool):
    """
    Wrapper around the Mouse Phenome Database (MPD) API for project searches.
    """

    def __init__(self, tool_config):
        super().__init__(tool_config)
        self.session = requests.Session()

    def run(self, arguments):
        keyword = (arguments or {}).get("keyword") or (arguments or {}).get("query")
        limit = int(
            (arguments or {}).get("limit") or self.tool_config.get("limit", 20)
        )

        params = {"limit": max(limit, 1)}
        if keyword:
            params["keyword"] = keyword

        response = self.session.get(
            f"{PHENOME_JAX_BASE_URL}/projects",
            params=params,
            timeout=REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()

        projects = []
        for item in payload.get("projects", []):
            projects.append(
                {
                    "projid": item.get("projid"),
                    "title": item.get("title"),
                    "mpdsector": item.get("mpdsector"),
                    "species": item.get("species"),
                    "status": item.get("status"),
                    "releasedate": item.get("releasedate"),
                }
            )

        return {
            "count": payload.get("count", len(projects)),
            "projects": projects[: params["limit"]],
        }
