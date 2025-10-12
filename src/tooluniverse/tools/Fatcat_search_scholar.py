"""
Fatcat_search_scholar

Search Internet Archive Scholar via Fatcat releases search. Fatcat is the underlying database powering Internet Archive Scholar, providing access to millions of research papers and academic publications.
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


def Fatcat_search_scholar(
    query: str,
    max_results: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search Internet Archive Scholar via Fatcat releases search. Fatcat is the underlying database powering Internet Archive Scholar, providing access to millions of research papers and academic publications.

    Parameters
    ----------
    query : str
        Search query for Fatcat releases. Use keywords to search across titles, abstracts, and metadata of research papers.
    max_results : int
        Maximum number of results to return. Default is 10, maximum is 100.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    list[Any]
    """
    return _get_client().run_one_function(
        {
            "name": "Fatcat_search_scholar",
            "arguments": {"query": query, "max_results": max_results},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Fatcat_search_scholar"]
