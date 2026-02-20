"""
Jikan_search_manga

Search for manga on MyAnimeList via the Jikan API. Returns manga titles matching a query with sco...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Jikan_search_manga(
    q: str,
    type_: Optional[str | Any] = None,
    status: Optional[str | Any] = None,
    order_by: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for manga on MyAnimeList via the Jikan API. Returns manga titles matching a query with sco...

    Parameters
    ----------
    q : str
        Search query for manga title (e.g., 'one piece', 'berserk', 'dragon ball')
    type_ : str | Any
        Filter by manga type: 'manga', 'novel', 'lightnovel', 'oneshot', 'doujin', 'm...
    status : str | Any
        Filter by status: 'publishing', 'complete', 'hiatus', 'discontinued', 'upcoming'
    order_by : str | Any
        Order by: 'title', 'score', 'chapters', 'volumes', 'start_date', 'members', '...
    sort : str | Any
        Sort direction: 'desc' or 'asc'
    limit : int | Any
        Number of results (1-25, default: 10)
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
            "name": "Jikan_search_manga",
            "arguments": {
                "q": q,
                "type": type_,
                "status": status,
                "order_by": order_by,
                "sort": sort,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Jikan_search_manga"]
