"""
TimeAPI_get_current_time_by_coordinates

Get the current date and time for a geographic location (latitude/longitude) using the TimeAPI.io...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TimeAPI_get_current_time_by_coordinates(
    latitude: float,
    longitude: float,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current date and time for a geographic location (latitude/longitude) using the TimeAPI.io...

    Parameters
    ----------
    latitude : float
        Latitude in decimal degrees (-90 to 90). Examples: 40.7128 (New York), 51.507...
    longitude : float
        Longitude in decimal degrees (-180 to 180). Examples: -74.0060 (New York), -0...
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
            "name": "TimeAPI_get_current_time_by_coordinates",
            "arguments": {"latitude": latitude, "longitude": longitude},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TimeAPI_get_current_time_by_coordinates"]
