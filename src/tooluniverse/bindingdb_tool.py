"""
BindingDB API tool for ToolUniverse.

BindingDB is a public database of measured binding affinities,
focusing chiefly on interactions of proteins considered drug-targets
with small, drug-like molecules.

API Documentation: https://www.bindingdb.org/rwd/bind/BindingDBRESTfulAPI.jsp
No authentication required.
"""

import requests
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool
from .tool_registry import register_tool

# Base URL for BindingDB REST API
BINDINGDB_API_URL = "https://bindingdb.org/rest"


@register_tool("BindingDBTool")
class BindingDBTool(BaseTool):
    """
    Tool for querying BindingDB binding affinity database.

    BindingDB provides:
    - Protein-ligand binding affinity data (IC50, Ki, Kd)
    - Small molecule structures (SMILES)
    - Target protein information
    - Literature references

    No authentication required. Free public access.
    """

    def __init__(self, tool_config: Dict[str, Any]):
        super().__init__(tool_config)
        self.timeout: int = tool_config.get(
            "timeout", 60
        )  # Longer timeout for large queries
        self.parameter = tool_config.get("parameter", {})

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute BindingDB API call based on operation type."""
        operation = arguments.get("operation", "")

        if operation == "get_by_uniprot":
            return self._get_by_uniprot(arguments)
        elif operation == "get_by_pdb":
            return self._get_by_pdb(arguments)
        elif operation == "get_by_target_name":
            return self._get_by_target_name(arguments)
        else:
            return {
                "status": "error",
                "error": f"Unknown operation: {operation}. Supported: get_by_uniprot, get_by_pdb, get_by_target_name",
            }

    def _get_by_uniprot(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get binding data for a protein by UniProt accession.

        Args:
            arguments: Dict containing:
                - uniprot_id: UniProt accession (e.g., P00533 for EGFR)
                - affinity_cutoff: Max affinity in nM (default: 10000)
        """
        uniprot_id = arguments.get("uniprot_id", "")
        if not uniprot_id:
            return {
                "status": "error",
                "error": "Missing required parameter: uniprot_id",
            }

        affinity_cutoff = arguments.get("affinity_cutoff", 10000)

        try:
            response = requests.get(
                f"{BINDINGDB_API_URL}/getLigandsByUniprots",
                params={
                    "uniprot": uniprot_id,
                    "cutoff": affinity_cutoff,
                },
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "ToolUniverse/BindingDB",
                },
            )
            response.raise_for_status()

            # BindingDB returns tab-separated or JSON data
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                data = response.json()
            else:
                # Parse text response
                data = self._parse_text_response(response.text)

            return {
                "status": "success",
                "data": {
                    "uniprot_id": uniprot_id,
                    "affinity_cutoff_nM": affinity_cutoff,
                    "ligands": data
                    if isinstance(data, list)
                    else data.get("ligands", []),
                    "count": len(data)
                    if isinstance(data, list)
                    else data.get("count", 0),
                },
                "metadata": {
                    "source": "BindingDB",
                    "uniprot_id": uniprot_id,
                },
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    "status": "success",
                    "data": {"uniprot_id": uniprot_id, "ligands": [], "count": 0},
                    "metadata": {"note": "No binding data found for this UniProt ID"},
                }
            return {"status": "error", "error": f"HTTP error: {e.response.status_code}"}
        except requests.exceptions.Timeout:
            return {
                "status": "error",
                "error": "Request timed out. Try a higher affinity cutoff.",
            }
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"status": "error", "error": f"Unexpected error: {str(e)}"}

    def _get_by_pdb(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get binding data for proteins by PDB ID(s).

        Args:
            arguments: Dict containing:
                - pdb_ids: Single PDB ID or comma-separated list (e.g., "1ABC,2XYZ")
                - affinity_cutoff: Max affinity in nM (default: 100)
                - sequence_identity: Min sequence identity % (default: 90)
        """
        pdb_ids = arguments.get("pdb_ids", "")
        if not pdb_ids:
            return {"status": "error", "error": "Missing required parameter: pdb_ids"}

        affinity_cutoff = arguments.get("affinity_cutoff", 100)
        sequence_identity = arguments.get("sequence_identity", 90)

        try:
            response = requests.get(
                f"{BINDINGDB_API_URL}/getLigandsByPDBs",
                params={
                    "pdb": pdb_ids,
                    "cutoff": affinity_cutoff,
                    "identity": sequence_identity,
                },
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "ToolUniverse/BindingDB",
                },
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                data = response.json()
            else:
                data = self._parse_text_response(response.text)

            return {
                "status": "success",
                "data": {
                    "pdb_ids": pdb_ids,
                    "affinity_cutoff_nM": affinity_cutoff,
                    "sequence_identity": sequence_identity,
                    "ligands": data
                    if isinstance(data, list)
                    else data.get("ligands", []),
                    "count": len(data)
                    if isinstance(data, list)
                    else data.get("count", 0),
                },
                "metadata": {
                    "source": "BindingDB",
                    "pdb_ids": pdb_ids,
                },
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    "status": "success",
                    "data": {"pdb_ids": pdb_ids, "ligands": [], "count": 0},
                    "metadata": {"note": "No binding data found for these PDB IDs"},
                }
            return {"status": "error", "error": f"HTTP error: {e.response.status_code}"}
        except requests.exceptions.Timeout:
            return {"status": "error", "error": "Request timed out"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"status": "error", "error": f"Unexpected error: {str(e)}"}

    def _get_by_target_name(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Search BindingDB by target protein name.

        Args:
            arguments: Dict containing:
                - target_name: Protein target name (e.g., "EGFR", "kinase")
                - affinity_cutoff: Max affinity in nM (default: 1000)
        """
        target_name = arguments.get("target_name", "")
        if not target_name:
            return {
                "status": "error",
                "error": "Missing required parameter: target_name",
            }

        affinity_cutoff = arguments.get("affinity_cutoff", 1000)

        try:
            response = requests.get(
                f"{BINDINGDB_API_URL}/getLigandsByTargetName",
                params={
                    "targetName": target_name,
                    "cutoff": affinity_cutoff,
                },
                timeout=self.timeout,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "ToolUniverse/BindingDB",
                },
            )
            response.raise_for_status()

            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type:
                data = response.json()
            else:
                data = self._parse_text_response(response.text)

            return {
                "status": "success",
                "data": {
                    "target_name": target_name,
                    "affinity_cutoff_nM": affinity_cutoff,
                    "ligands": data
                    if isinstance(data, list)
                    else data.get("ligands", []),
                    "count": len(data)
                    if isinstance(data, list)
                    else data.get("count", 0),
                },
                "metadata": {
                    "source": "BindingDB",
                    "target_name": target_name,
                },
            }

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return {
                    "status": "success",
                    "data": {"target_name": target_name, "ligands": [], "count": 0},
                    "metadata": {"note": "No binding data found for this target"},
                }
            return {"status": "error", "error": f"HTTP error: {e.response.status_code}"}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": f"Request failed: {str(e)}"}
        except Exception as e:
            return {"status": "error", "error": f"Unexpected error: {str(e)}"}

    def _parse_text_response(self, text: str) -> List[Dict[str, Any]]:
        """Parse tab-separated text response from BindingDB."""
        lines = text.strip().split("\n")
        if len(lines) < 2:
            return []

        # First line is header
        headers = lines[0].split("\t")
        results = []

        for line in lines[1:]:
            values = line.split("\t")
            if len(values) >= len(headers):
                result = {}
                for i, header in enumerate(headers):
                    result[header] = values[i] if i < len(values) else ""
                results.append(result)

        return results
