"""
OpenNotify_get_iss_position

Get the current real-time position of the International Space Station (ISS) in latitude and longi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenNotify_get_iss_position(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current real-time position of the International Space Station (ISS) in latitude and longi...

    Parameters
    ----------
    No parameters
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
        {"name": "OpenNotify_get_iss_position", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenNotify_get_iss_position"]
