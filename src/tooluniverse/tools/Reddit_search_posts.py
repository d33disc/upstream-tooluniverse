"""
Reddit_search_posts

Search Reddit posts across all subreddits or within a specific subreddit using the public Reddit ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Reddit_search_posts(
    q: str,
    subreddit: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    t: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Reddit posts across all subreddits or within a specific subreddit using the public Reddit ...

    Parameters
    ----------
    q : str
        Search query string (e.g., 'python machine learning', 'best programming langu...
    subreddit : str | Any
        Restrict search to a specific subreddit (e.g., 'python', 'programming', 'scie...
    sort : str | Any
        Sort order: 'relevance' (default), 'hot', 'top', 'new', 'comments'
    t : str | Any
        Time filter for 'top' sort: 'hour', 'day', 'week', 'month', 'year', 'all'
    limit : int | Any
        Number of results to return (1-100, default: 25)
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
            "name": "Reddit_search_posts",
            "arguments": {
                "q": q,
                "subreddit": subreddit,
                "sort": sort,
                "t": t,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Reddit_search_posts"]
