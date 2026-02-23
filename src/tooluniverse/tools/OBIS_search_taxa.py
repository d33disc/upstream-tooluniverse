"""
OBIS_search_taxa

Resolve marine taxa by scientific name via OBIS /v3/taxon
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OBIS_search_taxa(
    scientificname: str,
    size: Optional[int] = 10,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Resolve marine taxa by scientific name via OBIS /v3/taxon

    Parameters
    ----------
    scientificname : str
        Scientific name to search, e.g., 'Gadus'
    size : int

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
            "name": "OBIS_search_taxa",
            "arguments": {"scientificname": scientificname, "size": size},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OBIS_search_taxa"]
