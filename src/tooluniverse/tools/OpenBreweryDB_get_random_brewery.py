"""
OpenBreweryDB_get_random_brewery

Get one or more random breweries from the Open Brewery DB. Returns brewery details including name...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenBreweryDB_get_random_brewery(
    size: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get one or more random breweries from the Open Brewery DB. Returns brewery details including name...

    Parameters
    ----------
    size : int | Any
        Number of random breweries to return (1-50). Default: 1
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
        {"name": "OpenBreweryDB_get_random_brewery", "arguments": {"size": size}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenBreweryDB_get_random_brewery"]
