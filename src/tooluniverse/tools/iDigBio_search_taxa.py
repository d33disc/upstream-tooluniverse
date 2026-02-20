"""
iDigBio_search_taxa

Search iDigBio for taxon-level summaries across digitized natural history collections. Returns ag...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iDigBio_search_taxa(
    scientificname: Optional[str | Any] = None,
    kingdom: Optional[str | Any] = None,
    family: Optional[str | Any] = None,
    genus: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search iDigBio for taxon-level summaries across digitized natural history collections. Returns ag...

    Parameters
    ----------
    scientificname : str | Any
        Scientific name to search for taxon records. Examples: 'Acer', 'Felidae', 'Or...
    kingdom : str | Any
        Kingdom filter: 'Plantae', 'Animalia', 'Fungi'
    family : str | Any
        Family filter. Example: 'Rosaceae'
    genus : str | Any
        Genus filter. Example: 'Rosa'
    limit : int | Any
        Number of results (default 10)
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
            "name": "iDigBio_search_taxa",
            "arguments": {
                "scientificname": scientificname,
                "kingdom": kingdom,
                "family": family,
                "genus": genus,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iDigBio_search_taxa"]
