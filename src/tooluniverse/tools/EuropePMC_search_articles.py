"""
EuropePMC_search_articles

Search for articles on Europe PMC including abstracts. The tool queries the Europe PMC web service using provided keywords and returns articles with details such as title, abstract, journal, publication year, and a URL to the full article.
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


def EuropePMC_search_articles(
    query: str,
    limit: Optional[int] = 5,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search for articles on Europe PMC including abstracts. The tool queries the Europe PMC web service using provided keywords and returns articles with details such as title, abstract, journal, publication year, and a URL to the full article.

    Parameters
    ----------
    query : str
        Search query for Europe PMC. Use keywords separated by spaces to refine your search.
    limit : int
        Number of articles to return. This sets the maximum number of articles retrieved from Europe PMC.
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
            "name": "EuropePMC_search_articles",
            "arguments": {"query": query, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["EuropePMC_search_articles"]
