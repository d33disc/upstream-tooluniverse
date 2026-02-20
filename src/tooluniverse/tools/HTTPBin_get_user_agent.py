"""
HTTPBin_get_user_agent

Get the User-Agent header of the requesting client using httpbin.org. No authentication required....
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HTTPBin_get_user_agent(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the User-Agent header of the requesting client using httpbin.org. No authentication required....

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
        {"name": "HTTPBin_get_user_agent", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HTTPBin_get_user_agent"]
