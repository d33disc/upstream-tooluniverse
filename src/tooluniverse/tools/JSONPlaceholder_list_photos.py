"""
JSONPlaceholder_list_photos

List photos from JSONPlaceholder fake REST API, filtered by album ID. Returns photo data includin...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JSONPlaceholder_list_photos(
    albumId: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List photos from JSONPlaceholder fake REST API, filtered by album ID. Returns photo data includin...

    Parameters
    ----------
    albumId : int
        Album ID (1-100) to get photos from. Required to avoid massive response.
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
        {"name": "JSONPlaceholder_list_photos", "arguments": {"albumId": albumId}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JSONPlaceholder_list_photos"]
