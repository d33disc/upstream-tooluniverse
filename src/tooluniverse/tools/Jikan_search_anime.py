"""
Jikan_search_anime

Search for anime on MyAnimeList via the Jikan API. Returns anime titles matching a query with sco...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Jikan_search_anime(
    q: str,
    type_: Optional[str | Any] = None,
    status: Optional[str | Any] = None,
    rating: Optional[str | Any] = None,
    order_by: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for anime on MyAnimeList via the Jikan API. Returns anime titles matching a query with sco...

    Parameters
    ----------
    q : str
        Search query for anime title (e.g., 'naruto', 'attack on titan', 'spirited aw...
    type_ : str | Any
        Filter by anime type: 'tv', 'movie', 'ova', 'special', 'ona', 'music', 'cm', ...
    status : str | Any
        Filter by airing status: 'airing', 'complete', 'upcoming'
    rating : str | Any
        Filter by age rating: 'g', 'pg', 'pg13', 'r17', 'r', 'rx'
    order_by : str | Any
        Order results by: 'title', 'score', 'episodes', 'start_date', 'end_date', 'me...
    sort : str | Any
        Sort direction: 'desc' or 'asc'
    limit : int | Any
        Number of results (1-25, default: 10)
    page : int | Any
        Page number for pagination
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
            "name": "Jikan_search_anime",
            "arguments": {
                "q": q,
                "type": type_,
                "status": status,
                "rating": rating,
                "order_by": order_by,
                "sort": sort,
                "limit": limit,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Jikan_search_anime"]
