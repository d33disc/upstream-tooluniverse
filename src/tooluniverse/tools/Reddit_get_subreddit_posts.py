"""
Reddit_get_subreddit_posts

Get top, hot, new, or rising posts from a specific subreddit using the public Reddit JSON API. No...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Reddit_get_subreddit_posts(
    subreddit: str,
    listing: str,
    t: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get top, hot, new, or rising posts from a specific subreddit using the public Reddit JSON API. No...

    Parameters
    ----------
    subreddit : str
        Subreddit name without r/ prefix (e.g., 'python', 'science', 'programming', '...
    listing : str
        Listing type: 'hot', 'new', 'top', or 'rising'
    t : str | Any
        Time filter for 'top' listing: 'hour', 'day', 'week', 'month', 'year', 'all'
    limit : int | Any
        Number of posts to return (1-100, default: 25)
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
            "name": "Reddit_get_subreddit_posts",
            "arguments": {
                "subreddit": subreddit,
                "listing": listing,
                "t": t,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Reddit_get_subreddit_posts"]
