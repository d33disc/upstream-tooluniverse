"""
SWAPI_get_people

Get Star Wars characters (people) data using the Star Wars API (SWAPI). Returns character details...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SWAPI_get_people(
    search: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Star Wars characters (people) data using the Star Wars API (SWAPI). Returns character details...

    Parameters
    ----------
    search : str | Any
        Search by character name. Examples: 'luke', 'vader', 'leia', 'yoda', 'obi-wan...
    page : int | Any
        Page number (10 results per page). Default: 1
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
        {"name": "SWAPI_get_people", "arguments": {"search": search, "page": page}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SWAPI_get_people"]
