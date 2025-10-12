"""
TRIP_Database_Guidelines_Search

Search TRIP Database (Turning Research into Practice) for evidence-based clinical guidelines. TRIP is a specialized clinical search engine that focuses on high-quality evidence-based content, particularly clinical guidelines from reputable sources worldwide.
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


def TRIP_Database_Guidelines_Search(
    query: str,
    limit: Optional[int] = 10,
    search_type: Optional[str] = "guideline",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search TRIP Database (Turning Research into Practice) for evidence-based clinical guidelines. TRIP is a specialized clinical search engine that focuses on high-quality evidence-based content, particularly clinical guidelines from reputable sources worldwide.

    Parameters
    ----------
    query : str
        Medical condition, treatment, or clinical question (e.g., 'diabetes management', 'stroke prevention', 'antibiotic therapy')
    limit : int
        Maximum number of guidelines to return (default: 10)
    search_type : str
        Type of content to search for (default: 'guideline'). Options include 'guideline', 'systematic-review', 'evidence-based-synopses'
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    return _get_client().run_one_function(
        {
            "name": "TRIP_Database_Guidelines_Search",
            "arguments": {"query": query, "limit": limit, "search_type": search_type},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TRIP_Database_Guidelines_Search"]
