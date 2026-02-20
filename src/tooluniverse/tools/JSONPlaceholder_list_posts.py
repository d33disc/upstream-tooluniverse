"""
JSONPlaceholder_list_posts

List posts from JSONPlaceholder fake REST API, optionally filtered by user ID. Returns an array o...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JSONPlaceholder_list_posts(
    userId: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List posts from JSONPlaceholder fake REST API, optionally filtered by user ID. Returns an array o...

    Parameters
    ----------
    userId : int | Any
        Filter posts by user ID (1-10). If omitted, returns all 100 posts.
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
        {"name": "JSONPlaceholder_list_posts", "arguments": {"userId": userId}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JSONPlaceholder_list_posts"]
