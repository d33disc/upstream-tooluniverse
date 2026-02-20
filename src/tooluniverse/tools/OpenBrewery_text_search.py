"""
OpenBrewery_text_search

Full-text search for breweries in the Open Brewery DB by keyword. Searches across brewery name, c...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenBrewery_text_search(
    query: str,
    per_page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Full-text search for breweries in the Open Brewery DB by keyword. Searches across brewery name, c...

    Parameters
    ----------
    query : str
        Search term to find breweries. Examples: 'stone brewing', 'lagunitas', 'new e...
    per_page : int | Any
        Number of results (default 5, max 10)
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
        {
            "name": "OpenBrewery_text_search",
            "arguments": {"query": query, "per_page": per_page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenBrewery_text_search"]
