"""
HPA_search_genes_by_query

Search for matching genes by gene name, keywords, or cell line names and return Ensembl ID list. This is the entry tool for many HPA query workflows.
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


def HPA_search_genes_by_query(
    search_query: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for matching genes by gene name, keywords, or cell line names and return Ensembl ID list. This is the entry tool for many HPA query workflows.

    Parameters
    ----------
    search_query : str
        Gene name, alias, keyword, or cell line name to search for, e.g., 'EGFR', 'TP53', or 'MCF7'.
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
            "name": "HPA_search_genes_by_query",
            "arguments": {"search_query": search_query},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HPA_search_genes_by_query"]
