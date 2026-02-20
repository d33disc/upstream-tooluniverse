"""
Cataas_get_random_cat

Get a random cat image from the Cat as a Service (CATAAS) API. Returns metadata about a random ca...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Cataas_get_random_cat(
    tag: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random cat image from the Cat as a Service (CATAAS) API. Returns metadata about a random ca...

    Parameters
    ----------
    tag : str | Any
        Filter by tag (e.g., 'cute', 'funny', 'sleeping', 'black', 'orange', 'kitten'...
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
        {"name": "Cataas_get_random_cat", "arguments": {"tag": tag}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Cataas_get_random_cat"]
