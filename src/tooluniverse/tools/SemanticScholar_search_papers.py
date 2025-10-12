"""
SemanticScholar_search_papers

Search for papers on Semantic Scholar including abstracts. This tool queries the Semantic Scholar API using natural language keywords and returns papers with details such as title, abstract, publication year, journal (venue), and URL.
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


def SemanticScholar_search_papers(
    query: str,
    limit: Optional[int] = 5,
    api_key: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search for papers on Semantic Scholar including abstracts. This tool queries the Semantic Scholar API using natural language keywords and returns papers with details such as title, abstract, publication year, journal (venue), and URL.

    Parameters
    ----------
    query : str
        Search query for Semantic Scholar. Use keywords separated by spaces to refine the search.
    limit : int
        Maximum number of papers to return from Semantic Scholar.
    api_key : str
        Optional API key for Semantic Scholar to obtain a higher quota.
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
            "name": "SemanticScholar_search_papers",
            "arguments": {"query": query, "limit": limit, "api_key": api_key},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SemanticScholar_search_papers"]
