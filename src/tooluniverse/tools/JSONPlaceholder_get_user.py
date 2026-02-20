"""
JSONPlaceholder_get_user

Get a specific user profile by ID from JSONPlaceholder fake REST API. Returns detailed user data ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JSONPlaceholder_get_user(
    user_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a specific user profile by ID from JSONPlaceholder fake REST API. Returns detailed user data ...

    Parameters
    ----------
    user_id : int
        User ID to retrieve (1-10)
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
        {"name": "JSONPlaceholder_get_user", "arguments": {"user_id": user_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JSONPlaceholder_get_user"]
