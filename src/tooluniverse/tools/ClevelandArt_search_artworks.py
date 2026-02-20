"""
ClevelandArt_search_artworks

Search the Cleveland Museum of Art's open access collection of 61,000+ artworks through their pub...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ClevelandArt_search_artworks(
    q: Optional[str | Any] = None,
    department: Optional[str | Any] = None,
    type_: Optional[str | Any] = None,
    culture: Optional[str | Any] = None,
    technique: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    skip: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Cleveland Museum of Art's open access collection of 61,000+ artworks through their pub...

    Parameters
    ----------
    q : str | Any
        Search query. Examples: 'van gogh', 'chinese bronze', 'impressionism', 'portr...
    department : str | Any
        Filter by department. Examples: 'Egyptian and Ancient Near Eastern Art', 'Eur...
    type_ : str | Any
        Filter by artwork type. Examples: 'Painting', 'Sculpture', 'Drawing', 'Print'...
    culture : str | Any
        Filter by culture. Examples: 'American', 'French', 'Chinese', 'Japanese', 'Eg...
    technique : str | Any
        Filter by technique. Examples: 'Oil on canvas', 'Watercolor', 'Bronze casting'
    limit : int | Any
        Number of results (default 10, max 1000)
    skip : int | Any
        Number of records to skip for pagination
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
            "name": "ClevelandArt_search_artworks",
            "arguments": {
                "q": q,
                "department": department,
                "type": type_,
                "culture": culture,
                "technique": technique,
                "limit": limit,
                "skip": skip,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ClevelandArt_search_artworks"]
