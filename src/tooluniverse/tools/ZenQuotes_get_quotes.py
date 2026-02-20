"""
ZenQuotes_get_quotes

Get a batch of 50 inspirational quotes from ZenQuotes.io. Returns multiple quotes with authors fo...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ZenQuotes_get_quotes(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a batch of 50 inspirational quotes from ZenQuotes.io. Returns multiple quotes with authors fo...

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
        {"name": "ZenQuotes_get_quotes", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ZenQuotes_get_quotes"]
