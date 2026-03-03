"""
CIViC (Clinical Interpretation of Variants in Cancer) API tool for ToolUniverse.

CIViC is a community knowledgebase for expert-curated interpretations of variants
in cancer. It provides clinical evidence levels and interpretations.

API Documentation: https://civicdb.org/api
GraphQL Endpoint: https://civicdb.org/api/graphql
"""

import requests
from typing import Dict, Any, Optional
from .base_tool import BaseTool
from .tool_registry import register_tool

# Base URL for CIViC
CIVIC_BASE_URL = "https://civicdb.org/api"
CIVIC_GRAPHQL_URL = f"{CIVIC_BASE_URL}/graphql"


@register_tool("CIViCTool")
class CIViCTool(BaseTool):
    """
    Tool for querying CIViC (Clinical Interpretation of Variants in Cancer).

    CIViC provides:
    - Expert-curated cancer variant interpretations
    - Clinical evidence levels
    - Drug-variant associations
    - Disease-variant associations

    Uses GraphQL API. No authentication required. Free for academic/research use.
    """

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        fields = tool_config.get("fields", {})
        self.query_template: str = fields.get("query", "")
        self.operation_name: Optional[str] = fields.get("operation_name")
        self.timeout: int = tool_config.get("timeout", 30)
        # array_wrap: maps argument name -> GraphQL variable name, wrapping string in a list
        # e.g. {"gene_symbol": "entrezSymbols"} means arguments["gene_symbol"] -> variables["entrezSymbols"] = [value]
        self.array_wrap: Dict[str, str] = fields.get("array_wrap", {})

    def _build_graphql_query(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Build GraphQL query from template and arguments."""
        query = self.query_template

        # GraphQL queries use variables, not string replacement
        # Extract variable names from query (e.g., $limit, $gene_id)
        import re

        var_matches = re.findall(r"\$(\w+)", query)

        # Map arguments to GraphQL variables
        # GraphQL variable names match argument names in our config
        variables = {}
        for var_name in var_matches:
            # Check if argument exists (variable name matches argument name)
            if var_name in arguments:
                variables[var_name] = arguments[var_name]

        # Handle array_wrap: convert string arguments to lists for array-typed GraphQL variables
        for arg_name, var_name in self.array_wrap.items():
            if arg_name in arguments and arguments[arg_name] is not None:
                val = arguments[arg_name]
                variables[var_name] = [val] if not isinstance(val, list) else val

        payload = {"query": query}

        if self.operation_name:
            payload["operationName"] = self.operation_name

        if variables:
            payload["variables"] = variables

        return payload

    def _lookup_gene_id(self, gene_name: str) -> Optional[int]:
        """Look up CIViC gene ID by gene symbol via GraphQL."""
        payload = {
            "query": "query GetGenes($entrezSymbols: [String!]) { genes(entrezSymbols: $entrezSymbols) { nodes { id name } } }",
            "variables": {"entrezSymbols": [gene_name.upper()]},
        }
        try:
            resp = requests.post(
                CIVIC_GRAPHQL_URL,
                json=payload,
                timeout=10,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            data = resp.json().get("data", {})
            nodes = data.get("genes", {}).get("nodes", [])
            if nodes:
                return nodes[0]["id"]
        except Exception:
            pass
        return None

    def _get_variants_for_gene_id(
        self, gene_id: int, limit: int = 50
    ) -> Dict[str, Any]:
        """Fetch variants for a given CIViC gene_id via GraphQL."""
        payload = {
            "query": "query GetVariantsByGene($gene_id: Int!, $limit: Int) { gene(id: $gene_id) { id name variants(first: $limit) { nodes { id name } } } }",
            "operationName": "GetVariantsByGene",
            "variables": {"gene_id": gene_id, "limit": limit},
        }
        try:
            resp = requests.post(
                CIVIC_GRAPHQL_URL,
                json=payload,
                timeout=30,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
            )
            data = resp.json().get("data", {})
            return {
                "data": data,
                "metadata": {"source": "CIViC", "format": "GraphQL"},
            }
        except Exception as e:
            return {"error": f"CIViC API request failed: {str(e)}"}

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the CIViC GraphQL API call."""
        tool_name = self.tool_config.get("name", "")

        # civic_get_variants_by_gene: resolve gene_name → gene_id if needed
        if tool_name == "civic_get_variants_by_gene":
            if not arguments.get("gene_id"):
                gene_name = (
                    arguments.get("gene_name")
                    or arguments.get("gene")
                    or arguments.get("query")
                )
                if not gene_name:
                    return {
                        "error": "gene_id or gene_name is required for civic_get_variants_by_gene"
                    }
                gene_id = self._lookup_gene_id(gene_name)
                if gene_id is None:
                    return {"error": f"Gene '{gene_name}' not found in CIViC database"}
                arguments = dict(arguments)
                arguments["gene_id"] = gene_id
            return self._get_variants_for_gene_id(
                arguments["gene_id"], arguments.get("limit", 50)
            )

        # civic_search_variants: if gene/gene_name provided, look up gene_id then get variants
        if tool_name == "civic_search_variants":
            gene_name = arguments.get("gene") or arguments.get("gene_name")
            if gene_name and not arguments.get("query"):
                gene_id = self._lookup_gene_id(gene_name)
                if gene_id is None:
                    return {"error": f"Gene '{gene_name}' not found in CIViC database"}
                return self._get_variants_for_gene_id(
                    gene_id, arguments.get("limit", 50)
                )

        try:
            # Build GraphQL query
            payload = self._build_graphql_query(arguments)

            # Make GraphQL request
            response = requests.post(
                CIVIC_GRAPHQL_URL,
                json=payload,
                timeout=self.timeout,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "User-Agent": "ToolUniverse/CIViC",
                },
            )

            response.raise_for_status()
            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                return {
                    "error": "GraphQL query errors",
                    "errors": data["errors"],
                    "query": arguments,
                }

            return {
                "data": data.get("data", {}),
                "metadata": {
                    "source": "CIViC (Clinical Interpretation of Variants in Cancer)",
                    "format": "GraphQL",
                    "endpoint": CIVIC_GRAPHQL_URL,
                },
            }

        except requests.RequestException as e:
            return {"error": f"CIViC API request failed: {str(e)}", "query": arguments}
        except ValueError as e:
            return {"error": str(e), "query": arguments}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}", "query": arguments}
