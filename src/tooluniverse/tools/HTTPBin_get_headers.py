"""
HTTPBin_get_headers

Get the request headers as seen by the server using httpbin.org. Returns all HTTP headers sent in...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HTTPBin_get_headers(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the request headers as seen by the server using httpbin.org. Returns all HTTP headers sent in...

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
        {"name": "HTTPBin_get_headers", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HTTPBin_get_headers"]
