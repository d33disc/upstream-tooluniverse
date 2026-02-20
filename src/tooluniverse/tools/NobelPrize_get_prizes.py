"""
NobelPrize_get_prizes

Search and retrieve Nobel Prize records from the official Nobel Prize API. Returns prize details ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NobelPrize_get_prizes(
    yearFrom: Optional[int | Any] = None,
    yearTo: Optional[int | Any] = None,
    nobelPrizeCategory: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search and retrieve Nobel Prize records from the official Nobel Prize API. Returns prize details ...

    Parameters
    ----------
    yearFrom : int | Any
        Filter prizes from this year (inclusive). Example: 2010
    yearTo : int | Any
        Filter prizes up to this year (inclusive). Example: 2023
    nobelPrizeCategory : str | Any
        Filter by category. Values: 'che' (Chemistry), 'eco' (Economics), 'lit' (Lite...
    sort : str | Any
        Sort order: 'asc' or 'desc' by year (default: 'asc')
    limit : int | Any
        Number of prizes to return (default 25, max 100)
    offset : int | Any
        Offset for pagination (default 0)
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
            "name": "NobelPrize_get_prizes",
            "arguments": {
                "yearFrom": yearFrom,
                "yearTo": yearTo,
                "nobelPrizeCategory": nobelPrizeCategory,
                "sort": sort,
                "limit": limit,
                "offset": offset,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NobelPrize_get_prizes"]
