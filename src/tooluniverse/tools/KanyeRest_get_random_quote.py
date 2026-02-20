"""
KanyeRest_get_random_quote

Get a random Kanye West quote from the Kanye REST API (api.kanye.rest). Returns a single randomly...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def KanyeRest_get_random_quote(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random Kanye West quote from the Kanye REST API (api.kanye.rest). Returns a single randomly...

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
        {"name": "KanyeRest_get_random_quote", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["KanyeRest_get_random_quote"]
