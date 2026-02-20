"""
WhereTheISSAt_get_position

Get the current position and velocity of the International Space Station (ISS) using the Where th...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def WhereTheISSAt_get_position(
    units: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current position and velocity of the International Space Station (ISS) using the Where th...

    Parameters
    ----------
    units : str | Any
        Unit system for distance/velocity. Values: 'kilometers', 'miles'. Default: ki...
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
        {"name": "WhereTheISSAt_get_position", "arguments": {"units": units}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["WhereTheISSAt_get_position"]
