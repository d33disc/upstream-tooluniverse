"""
HTTPBin_generate_uuid

Generate a random UUID (v4) using the httpbin.org service. Returns a universally unique identifie...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def HTTPBin_generate_uuid(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generate a random UUID (v4) using the httpbin.org service. Returns a universally unique identifie...

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
        {"name": "HTTPBin_generate_uuid", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["HTTPBin_generate_uuid"]
