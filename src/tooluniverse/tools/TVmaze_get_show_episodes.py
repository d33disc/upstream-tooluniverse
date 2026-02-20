"""
TVmaze_get_show_episodes

Get all episodes of a TV show by TVmaze show ID using the TVmaze API. Returns episode list with n...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TVmaze_get_show_episodes(
    show_id: int,
    specials: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get all episodes of a TV show by TVmaze show ID using the TVmaze API. Returns episode list with n...

    Parameters
    ----------
    show_id : int
        TVmaze show ID. Examples: 169 (Game of Thrones), 82 (Game of Thrones alt), 66...
    specials : int | Any
        Include special episodes (1=yes, 0=no). Default: 0
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
            "name": "TVmaze_get_show_episodes",
            "arguments": {"show_id": show_id, "specials": specials},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TVmaze_get_show_episodes"]
