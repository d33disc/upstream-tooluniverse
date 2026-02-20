"""
Lemmy_get_community_posts

Get posts from a specific Lemmy community (subreddit equivalent). Returns posts with titles, URLs...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Lemmy_get_community_posts(
    community_name: str,
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get posts from a specific Lemmy community (subreddit equivalent). Returns posts with titles, URLs...

    Parameters
    ----------
    community_name : str
        Community name to get posts from. Examples: 'technology', 'programming', 'lin...
    sort : str | Any
        Sort order. Values: 'Hot', 'New', 'Active', 'TopDay', 'TopWeek', 'TopMonth', ...
    limit : int | Any
        Number of posts (1-50). Default: 10
    page : int | Any
        Page number for pagination. Default: 1
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
            "name": "Lemmy_get_community_posts",
            "arguments": {
                "community_name": community_name,
                "sort": sort,
                "limit": limit,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Lemmy_get_community_posts"]
