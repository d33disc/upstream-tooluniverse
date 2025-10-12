"""
HPA_get_contextual_biological_process_analysis

Analyze a gene's biological processes in the context of a specific tissue or cell line by integrating functional annotation with expression data to determine functional relevance.
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


def HPA_get_contextual_biological_process_analysis(
    gene_name: str,
    context_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyze a gene's biological processes in the context of a specific tissue or cell line by integrating functional annotation with expression data to determine functional relevance.

    Parameters
    ----------
    gene_name : str
        Gene name or symbol, e.g., 'TP53', 'EGFR', 'BRCA1'.
    context_name : str
        Name of the tissue or cell line to provide context, e.g., 'brain', 'liver', 'hela', 'mcf7'.
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
            "name": "HPA_get_contextual_biological_process_analysis",
            "arguments": {"gene_name": gene_name, "context_name": context_name},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_get_contextual_biological_process_analysis"]
