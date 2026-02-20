"""
HackerNews_search_stories

Search Hacker News stories, comments, and jobs using the Algolia HN Search API. Access 500K+ stor...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HackerNews_search_stories(
    query: str,
    tags: Optional[str | Any] = None,
    hitsPerPage: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Hacker News stories, comments, and jobs using the Algolia HN Search API. Access 500K+ stor...

    Parameters
    ----------
    query : str
        Search query. Examples: 'python programming', 'machine learning', 'startup', ...
    tags : str | Any
        Filter by content type. Values: 'story' (top-level posts), 'comment', 'ask_hn...
    hitsPerPage : int | Any
        Number of results to return (1-20). Default: 10
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
            "name": "HackerNews_search_stories",
            "arguments": {"query": query, "tags": tags, "hitsPerPage": hitsPerPage},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HackerNews_search_stories"]
