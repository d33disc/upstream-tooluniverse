"""
ZenQuotes_get_today

Get today's inspirational quote from ZenQuotes.io. Returns the same quote for all users on a give...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ZenQuotes_get_today(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get today's inspirational quote from ZenQuotes.io. Returns the same quote for all users on a give...

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
        {"name": "ZenQuotes_get_today", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ZenQuotes_get_today"]
