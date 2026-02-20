"""
Lobsters_get_stories

Get technology news stories from Lobste.rs, a curated technology-focused link aggregation site po...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Lobsters_get_stories(
    feed: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get technology news stories from Lobste.rs, a curated technology-focused link aggregation site po...

    Parameters
    ----------
    feed : str | Any
        Feed type. Values: 'hottest' (default, by votes + age), 'newest' (most recent...
    page : int | Any
        Page number for pagination. Default: 1. Each page has ~25 stories.
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
        {"name": "Lobsters_get_stories", "arguments": {"feed": feed, "page": page}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Lobsters_get_stories"]
