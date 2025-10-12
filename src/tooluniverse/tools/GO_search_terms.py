"""
GO_search_terms

Searches for Gene Ontology (GO) terms by a keyword using the GOlr search engine. Returns GO terms and related biological entities.
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


def GO_search_terms(
    query: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Searches for Gene Ontology (GO) terms by a keyword using the GOlr search engine. Returns GO terms and related biological entities.

    Parameters
    ----------
    query : str
        The keyword to search for, e.g., 'apoptosis' or 'kinase activity'.
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
        {"name": "GO_search_terms", "arguments": {"query": query}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GO_search_terms"]
