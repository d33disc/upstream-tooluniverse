"""
HPA_get_comparative_expression_by_gene_and_cellline

Compare the expression level differences of a gene between a specific cell line and healthy tissues using gene name and cell line name.
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


def HPA_get_comparative_expression_by_gene_and_cellline(
    gene_name: str,
    cell_line: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Compare the expression level differences of a gene between a specific cell line and healthy tissues using gene name and cell line name.

    Parameters
    ----------
    gene_name : str
        Gene name or gene symbol, e.g., 'TP53', 'BRCA1', 'EGFR', etc.
    cell_line : str
        Cell line name, supported cell lines include: ishikawa, hela, mcf7, a549, hepg2, jurkat, pc3, rh30, siha, u251.
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
            "name": "HPA_get_comparative_expression_by_gene_and_cellline",
            "arguments": {"gene_name": gene_name, "cell_line": cell_line},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_comparative_expression_by_gene_and_cellline"]
