"""
DOAJ_search_articles

Search DOAJ (Directory of Open Access Journals) for open-access articles. Returns articles with title, authors, year, DOI, venue, and URL.
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


def DOAJ_search_articles(
    query: str,
    max_results: Optional[int] = 10,
    type: Optional[str] = "articles",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search DOAJ (Directory of Open Access Journals) for open-access articles. Returns articles with title, authors, year, DOI, venue, and URL.

    Parameters
    ----------
    query : str
        Search query for DOAJ articles. Supports Lucene syntax for advanced queries.
    max_results : int
        Maximum number of articles to return. Default is 10, maximum is 100.
    type : str
        Type of search: 'articles' or 'journals'. Default is 'articles'.
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
            "name": "DOAJ_search_articles",
            "arguments": {"query": query, "max_results": max_results, "type": type},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DOAJ_search_articles"]
