"""
4DN Data Portal API Tool

This tool provides access to the 4D Nucleome Data Portal, which hosts
350+ uniformly processed Hi-C contact files and chromatin conformation data.
"""

import requests
from typing import Dict, Any
from .base_tool import BaseTool
from .tool_registry import register_tool


FOURDN_BASE_URL = "https://data.4dnucleome.org"


@register_tool("FourDNTool")
class FourDNTool(BaseTool):
    """
    4DN Data Portal API tool for accessing Hi-C and chromatin conformation data.
    """

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments."""
        try:
            operation = arguments.get("operation", "search")

            if operation == "search":
                return self._search(arguments)
            elif operation == "get_file_metadata":
                return self._get_file_metadata(arguments)
            elif operation == "get_experiment_metadata":
                return self._get_experiment_metadata(arguments)
            elif operation == "download_file_url":
                return self._download_file_url(arguments)
            else:
                return {"status": "error", "error": f"Unknown operation: {operation}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _search(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search 4DN data portal for files or experiments."""
        try:
            query = arguments.get("query", "*")
            item_type = arguments.get("item_type", "File")
            limit = arguments.get("limit", 25)

            # Build search URL
            url = f"{FOURDN_BASE_URL}/search/"
            params = {"type": item_type, "q": query, "limit": limit, "format": "json"}

            # Add filters
            if "file_type" in arguments:
                params["file_type"] = arguments["file_type"]
            if "assay_title" in arguments:
                params["assay_title"] = arguments["assay_title"]
            if "biosource_name" in arguments:
                params["biosource_name"] = arguments["biosource_name"]

            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            results = data.get("@graph", [])

            return {
                "status": "success",
                "num_results": len(results),
                "total": data.get("total", 0),
                "results": results[:limit],
                "search_url": response.url,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_file_metadata(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata for a specific file."""
        try:
            file_accession = arguments.get("file_accession")

            if not file_accession:
                return {"status": "error", "error": "file_accession is required"}

            url = f"{FOURDN_BASE_URL}/{file_accession}/?format=json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            return {
                "status": "success",
                "accession": file_accession,
                "file_type": data.get("file_type"),
                "file_format": data.get("file_format", {}).get("display_title"),
                "file_size": data.get("file_size"),
                "description": data.get("description"),
                "data_status": data.get("status"),
                "biosource": data.get("biosource"),
                "experiment": data.get("experiment"),
                "download_url": f"{FOURDN_BASE_URL}/{file_accession}/@@download",
                "metadata": data,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_experiment_metadata(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata for a specific experiment."""
        try:
            experiment_accession = arguments.get("experiment_accession")

            if not experiment_accession:
                return {"status": "error", "error": "experiment_accession is required"}

            url = f"{FOURDN_BASE_URL}/{experiment_accession}/?format=json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            data = response.json()

            return {
                "status": "success",
                "accession": experiment_accession,
                "experiment_type": data.get("experiment_type", {}).get("display_title"),
                "biosource": data.get("biosource"),
                "description": data.get("description"),
                "data_status": data.get("status"),
                "files": data.get("files", []),
                "metadata": data,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _download_file_url(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get download URL for a file (requires authentication for download)."""
        try:
            file_accession = arguments.get("file_accession")

            if not file_accession:
                return {"status": "error", "error": "file_accession is required"}

            # Get DRS API information
            drs_url = f"{FOURDN_BASE_URL}/ga4gh/drs/v1/objects/{file_accession}"

            return {
                "status": "success",
                "accession": file_accession,
                "download_url": f"{FOURDN_BASE_URL}/{file_accession}/@@download",
                "drs_url": drs_url,
                "note": "File download requires authentication. Use curl with access key: curl -O -L --user <key>:<secret> <download-url>",
                "instruction": "Create access key at https://data.4dnucleome.org/me",
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}
