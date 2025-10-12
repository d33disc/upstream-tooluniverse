"""
OpenAlex_Guidelines_Search

Search for clinical practice guidelines using OpenAlex scholarly database. Provides access to a comprehensive collection of guidelines from various sources worldwide, with citation metrics and institutional affiliations.
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


def OpenAlex_Guidelines_Search(
    query: str,
    limit: Optional[int] = 10,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search for clinical practice guidelines using OpenAlex scholarly database. Provides access to a comprehensive collection of guidelines from various sources worldwide, with citation metrics and institutional affiliations.

    Parameters
    ----------
    query : str
        Medical condition or clinical topic to search for guidelines (e.g., 'diabetes management', 'hypertension treatment', 'cancer screening')
    limit : int
        Maximum number of guidelines to return (default: 10)
    year_from : int
        Filter for guidelines published from this year onwards (optional)
    year_to : int
        Filter for guidelines published up to this year (optional)
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
            "name": "OpenAlex_Guidelines_Search",
            "arguments": {
                "query": query,
                "limit": limit,
                "year_from": year_from,
                "year_to": year_to,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenAlex_Guidelines_Search"]
