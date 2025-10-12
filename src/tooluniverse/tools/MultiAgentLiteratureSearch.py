"""
MultiAgentLiteratureSearch

Multi-agent literature search system that uses AI agents to analyze intent, extract keywords, execute parallel searches, summarize results, and check quality iteratively
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


def MultiAgentLiteratureSearch(
    query: str,
    max_iterations: Optional[int] = 3,
    quality_threshold: Optional[float] = 0.7,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Multi-agent literature search system that uses AI agents to analyze intent, extract keywords, execute parallel searches, summarize results, and check quality iteratively

    Parameters
    ----------
    query : str
        The research query to search for
    max_iterations : int
        Maximum number of iterations (default: 3)
    quality_threshold : float
        Quality threshold for completion (default: 0.7)
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    Any
    """
    return _get_client().run_one_function(
        {
            "name": "MultiAgentLiteratureSearch",
            "arguments": {
                "query": query,
                "max_iterations": max_iterations,
                "quality_threshold": quality_threshold,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MultiAgentLiteratureSearch"]
