"""
TVmaze_get_show

Get detailed information about a specific TV show from TVmaze using its ID. Returns comprehensive...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TVmaze_get_show(
    show_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific TV show from TVmaze using its ID. Returns comprehensive...

    Parameters
    ----------
    show_id : int
        TVmaze show ID. Common IDs: 169 (Breaking Bad), 82 (Game of Thrones), 1871 (C...
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
        {"name": "TVmaze_get_show", "arguments": {"show_id": show_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TVmaze_get_show"]
