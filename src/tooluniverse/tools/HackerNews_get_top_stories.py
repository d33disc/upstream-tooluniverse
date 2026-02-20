"""
HackerNews_get_top_stories

Get the IDs of top, new, best, ask, show, or job stories from Hacker News using the official Fire...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HackerNews_get_top_stories(
    category: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the IDs of top, new, best, ask, show, or job stories from Hacker News using the official Fire...

    Parameters
    ----------
    category : str | Any
        Story category. Values: 'topstories' (default), 'newstories', 'beststories', ...
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
        {"name": "HackerNews_get_top_stories", "arguments": {"category": category}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HackerNews_get_top_stories"]
