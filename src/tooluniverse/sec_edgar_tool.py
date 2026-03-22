from typing import Any, Dict

import requests

from .base_rest_tool import BaseRESTTool
from .tool_registry import register_tool


@register_tool("SECEdgarRESTTool")
class SECEdgarRESTTool(BaseRESTTool):
    """REST tool for SEC EDGAR EFTS and submissions APIs."""

    def _get_param_mapping(self) -> Dict[str, str]:
        return {"query": "q"}

    def _process_response(
        self, response: requests.Response, url: str
    ) -> Dict[str, Any]:
        data = response.json()

        # EFTS search-index returns Elasticsearch-style hits
        if isinstance(data, dict) and "hits" in data:
            raw_hits = data.get("hits", {}).get("hits", [])
            filings = []
            for hit in raw_hits:
                src = hit.get("_source", {})
                filings.append(
                    {
                        "company": (src.get("display_names") or [""])[0],
                        "cik": (src.get("ciks") or [""])[0],
                        "form": src.get("form", ""),
                        "file_date": src.get("file_date", ""),
                        "accession": src.get("adsh", ""),
                    }
                )
            return {
                "status": "success",
                "data": filings,
                "count": len(filings),
                "url": url,
            }

        # Submissions endpoint returns company profile directly
        return {"status": "success", "data": data, "url": url}
