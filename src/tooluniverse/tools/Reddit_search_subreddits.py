"""
Reddit_search_subreddits

Search for subreddits by keyword using the public Reddit JSON API. Returns matching subreddits wi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Reddit_search_subreddits(
    q: str,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for subreddits by keyword using the public Reddit JSON API. Returns matching subreddits wi...

    Parameters
    ----------
    q : str
        Search query for subreddit names and descriptions (e.g., 'bioinformatics', 'd...
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
        {"name": "Reddit_search_subreddits", "arguments": {"q": q, "limit": limit}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Reddit_search_subreddits"]
