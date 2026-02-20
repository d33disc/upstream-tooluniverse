"""
BigDataCloud_reverse_geocode

Reverse geocode latitude/longitude coordinates to a human-readable location using BigDataCloud AP...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BigDataCloud_reverse_geocode(
    latitude: float,
    longitude: float,
    localityLanguage: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Reverse geocode latitude/longitude coordinates to a human-readable location using BigDataCloud AP...

    Parameters
    ----------
    latitude : float
        Latitude in decimal degrees (-90 to 90). Examples: 48.8566 (Paris), 40.7128 (...
    longitude : float
        Longitude in decimal degrees (-180 to 180). Examples: 2.3522 (Paris), -74.006...
    localityLanguage : str | Any
        Language code for locality names. Default: 'en'. Examples: 'en', 'fr', 'de', ...
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
            "name": "BigDataCloud_reverse_geocode",
            "arguments": {
                "latitude": latitude,
                "longitude": longitude,
                "localityLanguage": localityLanguage,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BigDataCloud_reverse_geocode"]
