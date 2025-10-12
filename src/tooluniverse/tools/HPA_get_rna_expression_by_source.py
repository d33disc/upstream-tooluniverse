"""
HPA_get_rna_expression_by_source

Get RNA expression level (nTPM) for a gene in a specific biological source using optimized columns parameter. Supports tissue, blood, brain, and single_cell source types with comprehensive source mappings.
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


def HPA_get_rna_expression_by_source(
    gene_name: str,
    source_type: str,
    source_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get RNA expression level (nTPM) for a gene in a specific biological source using optimized columns parameter. Supports tissue, blood, brain, and single_cell source types with comprehensive source mappings.

    Parameters
    ----------
    gene_name : str
        Gene name or gene symbol, e.g., 'GFAP', 'TP53', 'BRCA1', etc.
    source_type : str
        The type of biological source. Choose from: 'tissue', 'blood', 'brain', 'single_cell'.
    source_name : str
        The specific name of the biological source, e.g., 'liver', 'heart_muscle', 't_cell', 'hepatocytes', 'cerebellum'. Must be a valid name from the comprehensive HPA columns mapping.
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
    return _get_client().run_one_function(
        {
            "name": "HPA_get_rna_expression_by_source",
            "arguments": {
                "gene_name": gene_name,
                "source_type": source_type,
                "source_name": source_name,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_rna_expression_by_source"]
