"""
HackerNews_get_recent_stories

Get the most recent Hacker News stories using the Algolia HN Search API, sorted by recency. Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HackerNews_get_recent_stories(
    query: Optional[str | Any] = None,
    tags: Optional[str | Any] = None,
    hitsPerPage: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the most recent Hacker News stories using the Algolia HN Search API, sorted by recency. Retur...

    Parameters
    ----------
    query : str | Any
        Optional search query to filter recent stories. Leave empty to get latest sto...
    tags : str | Any
        Filter by content type: 'story', 'ask_hn', 'show_hn', 'job'. Default: story
    hitsPerPage : int | Any
        Number of results (1-20). Default: 10
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
    # Handle mutable defaults to avoid B006 linting error

    return get_shared_client().run_one_function(
        {
            "name": "HackerNews_get_recent_stories",
            "arguments": {"query": query, "tags": tags, "hitsPerPage": hitsPerPage},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HackerNews_get_recent_stories"]
