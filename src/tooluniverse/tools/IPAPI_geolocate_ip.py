"""
IPAPI_geolocate_ip

Geolocate an IP address to get country, city, ISP, and timezone information using the ip-api.com ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def IPAPI_geolocate_ip(
    ip: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Geolocate an IP address to get country, city, ISP, and timezone information using the ip-api.com ...

    Parameters
    ----------
    ip : str
        IPv4 or IPv6 address to geolocate. Examples: '8.8.8.8' (Google DNS), '1.1.1.1...
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
        {"name": "IPAPI_geolocate_ip", "arguments": {"ip": ip}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["IPAPI_geolocate_ip"]
