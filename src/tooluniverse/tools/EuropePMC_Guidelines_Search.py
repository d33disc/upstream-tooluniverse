"""
EuropePMC_Guidelines_Search

Search Europe PMC for clinical guidelines and evidence-based recommendations. Europe PMC provides free access to a comprehensive archive of life sciences literature, including clinical practice guidelines from international sources.
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


def EuropePMC_Guidelines_Search(
    query: str,
    limit: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search Europe PMC for clinical guidelines and evidence-based recommendations. Europe PMC provides free access to a comprehensive archive of life sciences literature, including clinical practice guidelines from international sources.

    Parameters
    ----------
    query : str
        Medical condition, treatment, or clinical topic to search for (e.g., 'diabetes', 'cardiovascular disease', 'mental health')
    limit : int
        Maximum number of guidelines to return (default: 10)
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
            "name": "EuropePMC_Guidelines_Search",
            "arguments": {"query": query, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["EuropePMC_Guidelines_Search"]
