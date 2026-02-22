"""
NASANeoWs_browse_asteroids

Browse the full catalog of near-Earth asteroids from NASA's NeoWs API. Returns paginated results ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASANeoWs_browse_asteroids(
    page: Optional[int | Any] = None,
    size: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Browse the full catalog of near-Earth asteroids from NASA's NeoWs API. Returns paginated results ...

    Parameters
    ----------
    page : int | Any
        Page number (0-indexed). Default: 0. Each page returns 20 asteroids.
    size : int | Any
        Number of results per page (default 20, max 20)
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
            "name": "NASANeoWs_browse_asteroids",
            "arguments": {"page": page, "size": size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASANeoWs_browse_asteroids"]
