"""
IPGeolocation_lookup

Look up geolocation information for an IP address. Returns country, region, city, ZIP code, latit...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def IPGeolocation_lookup(
    ip: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up geolocation information for an IP address. Returns country, region, city, ZIP code, latit...

    Parameters
    ----------
    ip : str
        IP address to look up (IPv4 or IPv6, e.g., '8.8.8.8', '1.1.1.1')
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
        {"name": "IPGeolocation_lookup", "arguments": {"ip": ip}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["IPGeolocation_lookup"]
