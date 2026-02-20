"""
MangaDex_search_manga

Search for manga series in the MangaDex public API. Returns manga titles, descriptions, publicati...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MangaDex_search_manga(
    title: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    status: Optional[str | Any] = None,
    contentRating: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for manga series in the MangaDex public API. Returns manga titles, descriptions, publicati...

    Parameters
    ----------
    title : str | Any
        Manga title to search for. Examples: 'one piece', 'naruto', 'attack on titan'...
    limit : int | Any
        Number of results (1-100). Default: 10
    status : str | Any
        Publication status filter. Values: 'ongoing', 'completed', 'hiatus', 'cancelled'
    contentRating : str | Any
        Content rating filter. Values: 'safe', 'suggestive', 'erotica'. Default retur...
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
            "name": "MangaDex_search_manga",
            "arguments": {
                "title": title,
                "limit": limit,
                "status": status,
                "contentRating": contentRating,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MangaDex_search_manga"]
