"""
enrichr_gene_enrichment_analysis

Perform gene enrichment analysis using Enrichr to find biological pathways, processes, and molecular functions associated with a list of genes. Returns connectivity paths between genes and enrichment terms.
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def enrichr_gene_enrichment_analysis(
    gene_list: list[Any],
    libs: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Perform gene enrichment analysis using Enrichr to find biological pathways, processes, and molecular functions associated with a list of genes. Returns connectivity paths between genes and enrichment terms.

    Parameters
    ----------
    gene_list : list[Any]
        List of gene names or symbols to analyze. At least 2 genes are required for path ranking analysis.
    libs : list[Any]
        List of enrichment libraries to use for analysis.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    Any
    """
    if libs is None:
        libs = [
            "WikiPathways_2024_Human",
            "Reactome_Pathways_2024",
            "MSigDB_Hallmark_2020",
            "GO_Molecular_Function_2023",
            "GO_Biological_Process_2023",
        ]

    return _get_client().run_one_function(
        {
            "name": "enrichr_gene_enrichment_analysis",
            "arguments": {"gene_list": gene_list, "libs": libs},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["enrichr_gene_enrichment_analysis"]
