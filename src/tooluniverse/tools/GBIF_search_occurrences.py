"""
GBIF_search_occurrences

Search occurrences via GBIF occurrence/search
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def GBIF_search_occurrences(
    taxonKey: Optional[int] = None,
    country: Optional[str] = None,
    hasCoordinate: Optional[bool] = True,
    limit: Optional[int] = 10,
    offset: Optional[int] = 0,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search occurrences via GBIF occurrence/search

    Parameters
    ----------
    taxonKey : int
        GBIF taxonKey filter
    country : str
        Country code, e.g., US
    hasCoordinate : bool

    limit : int

    offset : int

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
            "name": "GBIF_search_occurrences",
            "arguments": {
                "taxonKey": taxonKey,
                "country": country,
                "hasCoordinate": hasCoordinate,
                "limit": limit,
                "offset": offset,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["GBIF_search_occurrences"]
