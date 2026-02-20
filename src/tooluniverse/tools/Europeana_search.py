"""
Europeana_search

Search Europeana - Europe's digital platform for cultural heritage with 50+ million items from 3,...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Europeana_search(
    query: str,
    rows: Optional[int | Any] = None,
    start: Optional[int | Any] = None,
    qf: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    profile: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Europeana - Europe's digital platform for cultural heritage with 50+ million items from 3,...

    Parameters
    ----------
    query : str
        Search query. Supports field-specific search: 'what:painting', 'who:rembrandt...
    rows : int | Any
        Number of results to return (default 12, max 100)
    start : int | Any
        Start index for pagination (default 1)
    qf : str | Any
        Query filter. Examples: 'TYPE:IMAGE', 'TYPE:TEXT', 'TYPE:VIDEO', 'TYPE:SOUND'...
    sort : str | Any
        Sort field. Examples: 'europeana_id', 'timestamp_created', 'score'. Use with ...
    profile : str | Any
        Response profile: 'minimal' (basic fields), 'standard' (more fields), 'rich' ...
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
            "name": "Europeana_search",
            "arguments": {
                "query": query,
                "rows": rows,
                "start": start,
                "qf": qf,
                "sort": sort,
                "profile": profile,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Europeana_search"]
