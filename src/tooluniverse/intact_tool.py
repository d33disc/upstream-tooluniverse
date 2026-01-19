"""
IntAct Molecular Interaction Database Tool

This tool provides access to the IntAct database for protein-protein interactions,
molecular interactions, and interaction evidence.
"""

import requests
from typing import Any, Dict
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("IntActRESTTool")
class IntActRESTTool(BaseTool):
    """
    IntAct REST API tool.
    Generic wrapper for IntAct API endpoints defined in intact_tools.json.
    """

    def __init__(self, tool_config: Dict):
        super().__init__(tool_config)
        self.base_url = "https://www.ebi.ac.uk/intact/ws"
        self.session = requests.Session()
        self.session.headers.update(
            {"Accept": "application/json", "User-Agent": "ToolUniverse/1.0"}
        )
        self.timeout = 30

    def _build_url(self, args: Dict[str, Any]) -> str:
        """Build URL from endpoint template and arguments"""
        endpoint_template = self.tool_config["fields"].get("endpoint", "")
        tool_name = self.tool_config.get("name", "")

        if endpoint_template:
            url = endpoint_template
            # Replace placeholders in URL
            for k, v in args.items():
                url = url.replace(f"{{{k}}}", str(v))
            return url

        # Build URL based on tool name
        if tool_name == "intact_get_interactor":
            identifier = args.get("identifier", "")
            if identifier:
                return f"{self.base_url}/interactor/details/{identifier}"

        elif tool_name == "intact_get_interactions":
            identifier = args.get("identifier", "")
            if identifier:
                return f"{self.base_url}/interaction/findInteractions"

        elif tool_name == "intact_search_interactions":
            return f"{self.base_url}/interaction/find"

        elif tool_name == "intact_get_interaction_details":
            interaction_id = args.get("interaction_id", "")
            if interaction_id:
                return f"{self.base_url}/interaction/{interaction_id}"

        elif tool_name == "intact_get_interaction_network":
            identifier = args.get("identifier", "")
            if identifier:
                return f"{self.base_url}/interaction/network/{identifier}"

        return self.base_url

    def _build_params(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Build query parameters for IntAct API"""
        params = {}
        tool_name = self.tool_config.get("name", "")

        # For search operations
        if tool_name == "intact_search_interactions":
            if "query" in args:
                params["query"] = args["query"]
            else:
                params["query"] = "*"
            params["format"] = args.get("format", "json")

        # For interaction retrieval by identifier
        elif tool_name == "intact_get_interactions":
            identifier = args.get("identifier", "")
            if identifier:
                params["query"] = identifier
            params["format"] = args.get("format", "json")

        # For interactor retrieval
        elif tool_name == "intact_get_interactor":
            params["format"] = args.get("format", "json")

        # For interaction details
        elif tool_name == "intact_get_interaction_details":
            params["format"] = args.get("format", "json")

        # For network
        elif tool_name == "intact_get_interaction_network":
            if "format" in args:
                params["format"] = args["format"]
            else:
                params["format"] = "json"
            if "depth" in args:
                params["depth"] = args["depth"]

        return params

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the IntAct API call"""
        tool_name = self.tool_config.get("name", "")

        # Use EBI Search API as primary method since IntAct direct API is unreliable
        # EBI Search has an 'intact' domain that works reliably
        if tool_name in [
            "intact_get_interactions",
            "intact_search_interactions",
            "intact_get_interactor",
        ]:
            return self._use_ebi_search(arguments, tool_name)

        try:
            # Build URL
            url = self._build_url(arguments)

            # Build parameters
            params = self._build_params(arguments)

            # Make API request
            response = self.session.get(url, params=params, timeout=self.timeout)

            # Check if response is HTML (API endpoint not available)
            content_type = response.headers.get("content-type", "")
            if "text/html" in content_type:
                # Fallback to EBI Search
                return self._use_ebi_search(arguments, tool_name)

            response.raise_for_status()

            # Parse JSON response
            data = response.json()

            # Build response
            response_data = {
                "status": "success",
                "data": data,
                "url": response.url,
            }

            # Add count for list results
            if isinstance(data, list):
                response_data["count"] = len(data)
            elif isinstance(data, dict) and "data" in data:
                if isinstance(data["data"], list):
                    response_data["count"] = len(data["data"])

            return response_data

        except requests.exceptions.RequestException:
            # Fallback to EBI Search if direct API fails
            return self._use_ebi_search(arguments, tool_name)
        except Exception as e:
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "url": url if "url" in locals() else None,
            }

    def _use_ebi_search(
        self, arguments: Dict[str, Any], tool_name: str
    ) -> Dict[str, Any]:
        """Use EBI Search API as fallback for IntAct queries"""
        try:
            ebi_search_url = "https://www.ebi.ac.uk/ebisearch/ws/rest/intact"
            params = {"format": "json"}

            if tool_name == "intact_get_interactions":
                identifier = arguments.get("identifier", "")
                if identifier:
                    params["query"] = identifier
                    params["size"] = arguments.get("size", 25)
            elif tool_name == "intact_search_interactions":
                query = arguments.get("query", "*")
                params["query"] = query
                params["size"] = arguments.get("max", 25)
            elif tool_name == "intact_get_interactor":
                identifier = arguments.get("identifier", "")
                if identifier:
                    # Search for the interactor by ID
                    params["query"] = identifier
                    params["size"] = 10

            response = self.session.get(
                ebi_search_url, params=params, timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()

            # Transform EBI Search response to match expected format
            entries = data.get("entries", [])

            # Extract interaction IDs for easy access
            interaction_ids = []
            for entry in entries:
                interaction_id = entry.get("id", "")
                if interaction_id:
                    interaction_ids.append(interaction_id)

            # For interactor lookup, try to get more details if possible
            if tool_name == "intact_get_interactor" and entries:
                # Return first matching entry as interactor details
                return {
                    "status": "success",
                    "data": entries[0] if entries else {},
                    "url": response.url,
                    "count": len(entries),
                    "hitCount": data.get("hitCount", len(entries)),
                    "interaction_ids": interaction_ids[:10],  # First 10 IDs
                    "note": "Data retrieved via EBI Search API (IntAct domain). For detailed interactor info, use IntAct website.",
                }

            # For interaction queries, include interaction IDs
            response_data = {
                "status": "success",
                "data": entries,
                "url": response.url,
                "count": len(entries),
                "hitCount": data.get("hitCount", len(entries)),
                "interaction_ids": interaction_ids,  # All interaction IDs found
                "note": "Data retrieved via EBI Search API (IntAct domain). Use interaction_ids to get details with intact_get_interaction_details or intact_get_interaction_network.",
            }

            return response_data
        except Exception as e:
            return {
                "status": "error",
                "error": f"IntAct query failed (tried EBI Search fallback): {str(e)}",
            }
