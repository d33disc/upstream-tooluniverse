"""
GeoJS_get_geo

Get IP geolocation data from GeoJS. Returns geographic information for a given IP address includi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GeoJS_get_geo(
    ip: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get IP geolocation data from GeoJS. Returns geographic information for a given IP address includi...

    Parameters
    ----------
    ip : str
        IP address to geolocate. Examples: '8.8.8.8' (Google DNS), '1.1.1.1' (Cloudfl...
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
        {"name": "GeoJS_get_geo", "arguments": {"ip": ip}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GeoJS_get_geo"]
