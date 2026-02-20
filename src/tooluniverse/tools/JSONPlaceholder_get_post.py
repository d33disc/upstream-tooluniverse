"""
JSONPlaceholder_get_post

Get a specific post by ID from JSONPlaceholder, a free fake REST API for testing and prototyping....
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JSONPlaceholder_get_post(
    post_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a specific post by ID from JSONPlaceholder, a free fake REST API for testing and prototyping....

    Parameters
    ----------
    post_id : int
        Post ID to retrieve (1-100). Example: 1
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
        {"name": "JSONPlaceholder_get_post", "arguments": {"post_id": post_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JSONPlaceholder_get_post"]
