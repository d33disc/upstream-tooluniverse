"""
WoRMS_search_species

Search marine species in the World Register of Marine Species (WoRMS) by name. Returns up to `lim...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def WoRMS_search_species(
    query: str,
    limit: Optional[int] = 20,
    offset: Optional[int] = 1,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search marine species in the World Register of Marine Species (WoRMS) by name. Returns up to `lim...

    Parameters
    ----------
    query : str
        Species name or search term
    limit : int
        Maximum number of taxon records to return (default 20). Pages larger than 50 ...
    offset : int
        1-based index of the first record to return (default 1). Use with `limit` and...
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

    # Strip None values so optional parameters don't trigger schema validation errors
    _args = {
        k: v
        for k, v in {"query": query, "limit": limit, "offset": offset}.items()
        if v is not None
    }
    return get_shared_client().run_one_function(
        {
            "name": "WoRMS_search_species",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["WoRMS_search_species"]
