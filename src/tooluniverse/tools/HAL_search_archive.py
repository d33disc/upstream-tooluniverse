"""
HAL_search_archive

Search the French HAL open archive via its public API. Returns documents with title, authors, year, DOI, URL, abstract, and source.
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


def HAL_search_archive(
    query: str,
    max_results: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search the French HAL open archive via its public API. Returns documents with title, authors, year, DOI, URL, abstract, and source.

    Parameters
    ----------
    query : str
        Search query for HAL archive. Supports Lucene syntax for advanced queries.
    max_results : int
        Maximum number of documents to return. Default is 10, maximum is 100.
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
            "name": "HAL_search_archive",
            "arguments": {"query": query, "max_results": max_results},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HAL_search_archive"]
