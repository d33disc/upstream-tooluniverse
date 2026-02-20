"""
JSONPlaceholder_get_post_comments

Get comments for a specific post from JSONPlaceholder fake REST API. Returns comments with commen...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JSONPlaceholder_get_post_comments(
    post_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comments for a specific post from JSONPlaceholder fake REST API. Returns comments with commen...

    Parameters
    ----------
    post_id : int
        Post ID (1-100) to get comments for
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
            "name": "JSONPlaceholder_get_post_comments",
            "arguments": {"post_id": post_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JSONPlaceholder_get_post_comments"]
