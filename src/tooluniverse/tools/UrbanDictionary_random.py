"""
UrbanDictionary_random

Get random slang term definitions from Urban Dictionary. Returns a set of random definitions, use...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def UrbanDictionary_random(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get random slang term definitions from Urban Dictionary. Returns a set of random definitions, use...

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
        {"name": "UrbanDictionary_random", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["UrbanDictionary_random"]
