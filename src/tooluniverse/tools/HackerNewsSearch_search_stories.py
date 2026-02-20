"""
HackerNewsSearch_search_stories

Search Hacker News stories, Ask HN posts, Show HN posts, and comments via the Algolia HN Search A...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HackerNewsSearch_search_stories(
    query: str,
    tags: Optional[str | Any] = None,
    numericFilters: Optional[str | Any] = None,
    hitsPerPage: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Hacker News stories, Ask HN posts, Show HN posts, and comments via the Algolia HN Search A...

    Parameters
    ----------
    query : str
        Search query. Examples: 'machine learning', 'rust programming', 'Show HN', 'A...
    tags : str | Any
        Filter by tag. Values: 'story' (default), 'comment', 'ask_hn', 'show_hn', 'fr...
    numericFilters : str | Any
        Numeric filter string. Examples: 'points>100' (at least 100 upvotes), 'num_co...
    hitsPerPage : int | Any
        Results per page (1-50). Default: 20
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
            "name": "HackerNewsSearch_search_stories",
            "arguments": {
                "query": query,
                "tags": tags,
                "numericFilters": numericFilters,
                "hitsPerPage": hitsPerPage,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HackerNewsSearch_search_stories"]
