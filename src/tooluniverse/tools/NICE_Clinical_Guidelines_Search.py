"""
NICE_Clinical_Guidelines_Search

Search NICE (National Institute for Health and Care Excellence) clinical guidelines and evidence-based recommendations. Provides access to official NICE guidelines covering diagnosis, treatment, and care pathways for various medical conditions.
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


def NICE_Clinical_Guidelines_Search(
    query: str,
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> list[Any]:
    """
    Search NICE (National Institute for Health and Care Excellence) clinical guidelines and evidence-based recommendations. Provides access to official NICE guidelines covering diagnosis, treatment, and care pathways for various medical conditions.

    Parameters
    ----------
    query : str
        Medical condition, treatment, or clinical topic to search for in NICE guidelines (e.g., 'diabetes', 'hypertension', 'cancer screening')
    limit : int
        Maximum number of clinical guidelines to return (default: 10)
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
            "name": "NICE_Clinical_Guidelines_Search",
            "arguments": {"query": query, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NICE_Clinical_Guidelines_Search"]
