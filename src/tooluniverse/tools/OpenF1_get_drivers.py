"""
OpenF1_get_drivers

Get Formula 1 driver information for a specific session using the OpenF1 API. Returns driver deta...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenF1_get_drivers(
    session_key: int,
    driver_number: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Formula 1 driver information for a specific session using the OpenF1 API. Returns driver deta...

    Parameters
    ----------
    session_key : int
        Session identifier from OpenF1 API. Examples: 9158 (Monza 2023 Race), 9468 (M...
    driver_number : int | Any
        Optional filter by driver number. Examples: 1 (Verstappen), 44 (Hamilton), 16...
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
            "name": "OpenF1_get_drivers",
            "arguments": {"session_key": session_key, "driver_number": driver_number},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenF1_get_drivers"]
