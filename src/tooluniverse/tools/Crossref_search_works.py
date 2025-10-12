"""
Crossref_search_works

Search Crossref Works API for articles by keyword. Returns articles with title, abstract, journal, year, DOI, and URL. Supports filtering by publication type and date range.
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


def Crossref_search_works(
    query: str,
    limit: Optional[int] = 10,
    filter: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search Crossref Works API for articles by keyword. Returns articles with title, abstract, journal, year, DOI, and URL. Supports filtering by publication type and date range.

    Parameters
    ----------
    query : str
        Search query for Crossref works. Use keywords separated by spaces to refine your search.
    limit : int
        Number of articles to return. This sets the maximum number of articles retrieved from Crossref.
    filter : str
        Optional filter string for Crossref API. Examples: 'type:journal-article,from-pub-date:2020-01-01'
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
            "name": "Crossref_search_works",
            "arguments": {"query": query, "limit": limit, "filter": filter},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Crossref_search_works"]
