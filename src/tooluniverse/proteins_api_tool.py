"""
Proteins API Tool

This tool provides access to the EBI Proteins API for comprehensive protein
annotations, variation data, proteomics, and reference genome mappings.
"""

import requests
from typing import Any, Dict, Optional
from .base_tool import BaseTool
from .tool_registry import register_tool


@register_tool("ProteinsAPIRESTTool")
class ProteinsAPIRESTTool(BaseTool):
    """
    Proteins API REST tool.
    Generic wrapper for Proteins API endpoints defined in proteins_api_tools.json.
    """

    def __init__(self, tool_config: Dict):
        super().__init__(tool_config)
        self.base_url = "https://www.ebi.ac.uk/proteins/api"
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
            for k, v in args.items():
                url = url.replace(f"{{{k}}}", str(v))
            return url

        # Build URL based on tool name
        if tool_name == "proteins_api_get_protein":
            accession = args.get("accession", "")
            if accession:
                return f"{self.base_url}/proteins/{accession}"

        elif tool_name == "proteins_api_get_variants":
            accession = args.get("accession", "")
            if accession:
                # Try variations endpoint - may not be available for all proteins
                return f"{self.base_url}/proteins/{accession}/variations"

        elif tool_name == "proteins_api_get_proteomics":
            accession = args.get("accession", "")
            if accession:
                # Try proteomics endpoint, fallback to main protein endpoint
                return f"{self.base_url}/proteins/{accession}/proteomics"

        elif tool_name == "proteins_api_get_epitopes":
            accession = args.get("accession", "")
            if accession:
                # Try epitopes endpoint, fallback to main protein endpoint
                return f"{self.base_url}/proteins/{accession}/epitopes"

        elif tool_name == "proteins_api_search":
            # Proteins API search uses query parameter, not path
            return f"{self.base_url}/proteins/search"

        return self.base_url

    def _build_params(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Build query parameters for Proteins API"""
        params = {}
        tool_name = self.tool_config.get("name", "")

        if tool_name == "proteins_api_search":
            # Proteins API search - try different parameter formats
            # The API may require specific parameter names
            if "query" in args:
                # Try 'accession' or 'name' parameters instead
                query = args["query"]
                # If it looks like an accession, use accession parameter
                if query.startswith("P") and len(query) == 6:
                    params["accession"] = query
                else:
                    # Try name parameter
                    params["name"] = query
            if "size" in args:
                params["size"] = args["size"]
            if "offset" in args:
                params["offset"] = args["offset"]

        # Format parameter
        if "format" in args:
            params["format"] = args["format"]
        else:
            params["format"] = "json"

        return params

    def _extract_from_protein_endpoint(
        self, accession: str, tool_name: str
    ) -> Optional[Dict[str, Any]]:
        """Extract proteomics/epitopes data from main protein endpoint"""
        try:
            protein_url = f"{self.base_url}/proteins/{accession}"
            response = self.session.get(protein_url, timeout=self.timeout)
            response.raise_for_status()
            protein_data = response.json()

            # Extract relevant data based on tool name
            if tool_name == "proteins_api_get_proteomics":
                # Look for proteomics-related data in response
                proteomics_data = []

                # Check comments for proteomics information
                if "comments" in protein_data:
                    for comment in protein_data["comments"]:
                        comment_type = str(comment.get("commentType", "")).upper()
                        if any(
                            x in comment_type
                            for x in [
                                "PTM",
                                "MODIFIED",
                                "MASS",
                                "SPECTROMETRY",
                                "PROTEOMICS",
                            ]
                        ):
                            proteomics_data.append(comment)

                # Check features for proteomics-related features
                if "features" in protein_data:
                    for feature in protein_data["features"]:
                        feature_type = str(feature.get("type", "")).lower()
                        if any(
                            x in feature_type
                            for x in ["modified", "mutagenesis", "site", "variant"]
                        ):
                            proteomics_data.append(feature)

                return {
                    "status": "success",
                    "data": proteomics_data,
                    "url": response.url,
                    "count": len(proteomics_data),
                    "note": "Proteomics data extracted from main protein endpoint (proteomics endpoint not available). Includes PTM comments, modified residues, and related features.",
                    "fallback_used": True,
                    "source": "main_protein_endpoint",
                }

            elif tool_name == "proteins_api_get_epitopes":
                # Look for epitope-related data
                epitopes_data = []

                # Check comments for epitope information
                if "comments" in protein_data:
                    for comment in protein_data["comments"]:
                        comment_str = str(comment).lower()
                        comment_type = str(comment.get("commentType", "")).upper()
                        if "epitope" in comment_str or comment_type == "IMMUNOLOGY":
                            epitopes_data.append(comment)

                # Check features for epitope sites
                if "features" in protein_data:
                    for feature in protein_data["features"]:
                        feature_str = str(feature).lower()
                        feature_type = str(feature.get("type", "")).lower()
                        if "epitope" in feature_str or "epitope" in feature_type:
                            epitopes_data.append(feature)

                return {
                    "status": "success",
                    "data": epitopes_data,
                    "url": response.url,
                    "count": len(epitopes_data),
                    "note": "Epitope data extracted from main protein endpoint (epitopes endpoint not available). Includes immunology comments and epitope features if present.",
                    "fallback_used": True,
                    "source": "main_protein_endpoint",
                }
        except Exception:
            return None

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the Proteins API call"""
        tool_name = self.tool_config.get("name", "")
        try:
            url = self._build_url(arguments)
            params = self._build_params(arguments)

            response = self.session.get(url, params=params, timeout=self.timeout)

            # Handle proteomics/epitopes endpoints - fallback to main protein endpoint
            if tool_name in [
                "proteins_api_get_proteomics",
                "proteins_api_get_epitopes",
            ]:
                if response.status_code == 404:
                    fallback_result = self._extract_from_protein_endpoint(
                        arguments.get("accession", ""), tool_name
                    )
                    if fallback_result:
                        return fallback_result

            # Handle search endpoint which may not exist
            if tool_name == "proteins_api_search" and response.status_code == 400:
                return {
                    "status": "error",
                    "error": "Proteins API search endpoint may not be available. Use proteins_api_get_protein with a specific accession instead, or use EBI Search API with 'uniprot' domain.",
                    "url": response.url,
                    "suggestion": "Try using ebi_search_domain with domain='uniprot' and your query instead.",
                }

            response.raise_for_status()
            data = response.json()

            response_data = {
                "status": "success",
                "data": data,
                "url": response.url,
            }

            if isinstance(data, list):
                response_data["count"] = len(data)
            elif isinstance(data, dict):
                if "results" in data and isinstance(data["results"], list):
                    response_data["count"] = len(data["results"])

            return response_data

        except requests.exceptions.RequestException as e:
            tool_name = self.tool_config.get("name", "")

            # For proteomics/epitopes endpoints, try fallback
            if tool_name in [
                "proteins_api_get_proteomics",
                "proteins_api_get_epitopes",
            ]:
                if "404" in str(e):
                    fallback_result = self._extract_from_protein_endpoint(
                        arguments.get("accession", ""), tool_name
                    )
                    if fallback_result:
                        return fallback_result

            # For variations endpoint, it may not be available for all proteins
            if tool_name == "proteins_api_get_variants" and "404" in str(e):
                return {
                    "status": "error",
                    "error": "Variations not available for this protein. Variations endpoint may not be available for all proteins.",
                    "url": url if "url" in locals() else None,
                    "note": "Try using proteins_api_get_protein to get comprehensive protein information instead.",
                }
            return {
                "status": "error",
                "error": f"Proteins API error: {str(e)}",
                "url": url if "url" in locals() else None,
            }
        except Exception as e:
            tool_name = self.tool_config.get("name", "")
            return {
                "status": "error",
                "error": f"Unexpected error: {str(e)}",
                "url": url if "url" in locals() else None,
            }
