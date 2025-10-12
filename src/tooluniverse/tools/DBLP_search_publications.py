"""
DBLP_search_publications

Search DBLP Computer Science Bibliography for publications. Returns publications with title, authors, year, venue, URL, and electronic edition link.
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


def DBLP_search_publications(
    query: str,
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search DBLP Computer Science Bibliography for publications. Returns publications with title, authors, year, venue, URL, and electronic edition link.

    Parameters
    ----------
    query : str
        Search query for DBLP publications. Use keywords separated by spaces to refine your search.
    limit : int
        Number of publications to return. This sets the maximum number of publications retrieved from DBLP.
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
            "name": "DBLP_search_publications",
            "arguments": {"query": query, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DBLP_search_publications"]
