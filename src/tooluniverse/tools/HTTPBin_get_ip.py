"""
HTTPBin_get_ip

Get the origin (public) IP address of the requesting client using httpbin.org. No authentication ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HTTPBin_get_ip(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the origin (public) IP address of the requesting client using httpbin.org. No authentication ...

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
        {"name": "HTTPBin_get_ip", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HTTPBin_get_ip"]
