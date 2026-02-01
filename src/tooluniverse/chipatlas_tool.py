"""
ChIP-Atlas API Tool

This tool provides access to ChIP-Atlas, a data-mining suite for exploring
epigenomic landscapes with 433,000+ ChIP-seq, ATAC-seq, and Bisulfite-seq experiments.
"""

import requests
from typing import Dict, Any
from .base_tool import BaseTool
from .tool_registry import register_tool


CHIPATLAS_BASE_URL = "https://chip-atlas.org"
CHIPATLAS_DATA_URL = "https://chip-atlas.dbcls.jp/data"


@register_tool("ChIPAtlasTool")
class ChIPAtlasTool(BaseTool):
    """
    ChIP-Atlas API tool for accessing chromatin data.
    Provides enrichment analysis, peak browsing, and dataset search.
    """

    def run(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool with given arguments."""
        try:
            operation = arguments.get("operation", "enrichment_analysis")

            if operation == "enrichment_analysis":
                return self._enrichment_analysis(arguments)

            elif operation == "get_experiment_list":
                return self._get_experiment_list(arguments)

            elif operation == "get_peak_data":
                return self._get_peak_data(arguments)

            elif operation == "search_datasets":
                return self._search_datasets(arguments)

            else:
                return {"status": "error", "error": f"Unknown operation: {operation}"}

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _enrichment_analysis(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform enrichment analysis on genomic regions, motifs, or gene lists.
        Identifies proteins bound to input regions more often than expected.
        """
        try:
            # Prepare enrichment analysis parameters
            bed_data = arguments.get("bed_data")
            motif = arguments.get("motif")
            gene_list = arguments.get("gene_list")
            genome = arguments.get("genome", "hg38")
            antigen_class = arguments.get("antigen_class", "")
            cell_type_class = arguments.get("cell_type_class", "")
            threshold = arguments.get("threshold", "05")
            distance = arguments.get("distance", "5000")

            # Build API request
            # Note: The actual API endpoint needs to be discovered from ChIP-Atlas documentation
            # For now, we provide information about how to use it

            if bed_data:
                return {
                    "status": "success",
                    "message": "ChIP-Atlas Enrichment Analysis requires web form submission",
                    "instruction": f"Submit BED data to: {CHIPATLAS_BASE_URL}/enrichment_analysis",
                    "parameters": {
                        "genome": genome,
                        "antigen_class": antigen_class,
                        "cell_type_class": cell_type_class,
                        "threshold": threshold,
                    },
                    "note": "ChIP-Atlas enrichment API requires form-based submission. Use Python 'requests' library for programmatic access.",
                }
            elif motif:
                return {
                    "status": "success",
                    "message": "Submit motif for enrichment analysis",
                    "motif": motif,
                    "url": f"{CHIPATLAS_BASE_URL}/enrichment_analysis",
                    "note": "Motif should be in IUPAC nucleic acid notation (ATGCWSMKRYBDHVN)",
                }
            elif gene_list:
                return {
                    "status": "success",
                    "message": "Submit gene list for enrichment analysis",
                    "genes": gene_list if isinstance(gene_list, list) else [gene_list],
                    "distance_from_tss": distance,
                    "url": f"{CHIPATLAS_BASE_URL}/enrichment_analysis",
                    "note": "Use official gene symbols (HGNC, MGI, RGD, FlyBase, WormBase, SGD)",
                }
            else:
                return {
                    "status": "error",
                    "error": "One of bed_data, motif, or gene_list must be provided",
                }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_experiment_list(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get metadata for all ChIP-Atlas experiments."""
        try:
            # Download experimentList.tab
            url = f"{CHIPATLAS_DATA_URL}/metadata/experimentList.tab"
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse TSV
            lines = response.text.strip().split("\n")
            experiments = []

            # Filter by genome if specified
            genome = arguments.get("genome")
            antigen = arguments.get("antigen")
            cell_type = arguments.get("cell_type")
            limit = arguments.get("limit", 100)

            for line in lines:
                fields = line.split("\t")
                if len(fields) >= 9:
                    exp = {
                        "experiment_id": fields[0],
                        "genome": fields[1],
                        "track_type_class": fields[2],
                        "track_type": fields[3],
                        "cell_type_class": fields[4],
                        "cell_type": fields[5],
                        "cell_type_description": fields[6],
                        "processing_logs": fields[7],
                        "title": fields[8],
                    }

                    # Apply filters
                    if genome and exp["genome"] != genome:
                        continue
                    if antigen and antigen.lower() not in exp["track_type"].lower():
                        continue
                    if cell_type and cell_type.lower() not in exp["cell_type"].lower():
                        continue

                    experiments.append(exp)

                    if len(experiments) >= limit:
                        break

            return {
                "status": "success",
                "num_experiments": len(experiments),
                "experiments": experiments,
                "message": f"Showing first {limit} experiments"
                if len(experiments) >= limit
                else None,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _get_peak_data(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Get URL for peak-call data (BigWig or BED format)."""
        try:
            experiment_id = arguments.get("experiment_id")
            genome = arguments.get("genome", "hg38")
            threshold = arguments.get("threshold", "05")
            format_type = arguments.get("format", "bigwig")

            if not experiment_id:
                return {"status": "error", "error": "experiment_id is required"}

            if format_type.lower() == "bigwig":
                url = f"{CHIPATLAS_DATA_URL}/{genome}/eachData/bw/{experiment_id}.bw"
            elif format_type.lower() == "bed":
                url = f"{CHIPATLAS_DATA_URL}/{genome}/eachData/bed{threshold}/{experiment_id}.{threshold}.bed"
            elif format_type.lower() == "bigbed":
                url = f"{CHIPATLAS_DATA_URL}/{genome}/eachData/bb{threshold}/{experiment_id}.{threshold}.bb"
            else:
                return {
                    "status": "error",
                    "error": f"Invalid format: {format_type}. Use 'bigwig', 'bed', or 'bigbed'",
                }

            return {
                "status": "success",
                "experiment_id": experiment_id,
                "genome": genome,
                "format": format_type,
                "url": url,
                "message": "Use this URL to download peak data",
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}

    def _search_datasets(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Search for datasets by antigen or cell type."""
        try:
            antigen = arguments.get("antigen")
            cell_type = arguments.get("cell_type")
            genome = arguments.get("genome", "hg38")

            if not antigen and not cell_type:
                return {
                    "status": "error",
                    "error": "Either antigen or cell_type must be provided",
                }

            # Download antigenList.tab or celltypeList.tab
            if antigen:
                url = f"{CHIPATLAS_DATA_URL}/metadata/antigenList.tab"
                search_key = "antigen"
                search_value = antigen
            else:
                url = f"{CHIPATLAS_DATA_URL}/metadata/celltypeList.tab"
                search_key = "cell_type"
                search_value = cell_type

            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Parse TSV
            lines = response.text.strip().split("\n")
            results = []

            for line in lines:
                fields = line.split("\t")
                if len(fields) >= 5:
                    if antigen:
                        if (
                            fields[1] == genome
                            and search_value.lower() in fields[2].lower()
                        ):
                            results.append(
                                {
                                    "genome": fields[0],
                                    "class": fields[1],
                                    "name": fields[2],
                                    "num_experiments": fields[3],
                                    "experiment_ids": fields[4].split(",")[
                                        :10
                                    ],  # Show first 10
                                }
                            )
                    else:
                        if (
                            fields[0] == genome
                            and search_value.lower() in fields[2].lower()
                        ):
                            results.append(
                                {
                                    "genome": fields[0],
                                    "cell_type_class": fields[1],
                                    "cell_type": fields[2],
                                    "num_experiments": fields[3],
                                    "experiment_ids": fields[4].split(",")[
                                        :10
                                    ],  # Show first 10
                                }
                            )

            return {
                "status": "success",
                "search_key": search_key,
                "search_value": search_value,
                "genome": genome,
                "num_results": len(results),
                "results": results,
            }

        except Exception as e:
            return {"status": "error", "error": str(e)}
