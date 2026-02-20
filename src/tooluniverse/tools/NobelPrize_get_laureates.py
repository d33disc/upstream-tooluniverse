"""
NobelPrize_get_laureates

Search Nobel Prize laureates from the official Nobel Prize API. Returns detailed information abou...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NobelPrize_get_laureates(
    name: Optional[str | Any] = None,
    nobelPrizeYear: Optional[int | Any] = None,
    nobelPrizeCategory: Optional[str | Any] = None,
    gender: Optional[str | Any] = None,
    birthCountry: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Nobel Prize laureates from the official Nobel Prize API. Returns detailed information abou...

    Parameters
    ----------
    name : str | Any
        Search by laureate name (partial match). Examples: 'Einstein', 'Curie', 'CRISPR'
    nobelPrizeYear : int | Any
        Filter laureates who won in this year. Example: 2023
    nobelPrizeCategory : str | Any
        Filter by prize category. Values: 'che', 'eco', 'lit', 'pea', 'phy', 'med'
    gender : str | Any
        Filter by gender: 'male', 'female', 'org' (organization)
    birthCountry : str | Any
        Filter by birth country name. Example: 'France', 'Germany', 'United States of...
    sort : str | Any
        Sort: 'asc' or 'desc'
    limit : int | Any
        Number of results (default 25)
    offset : int | Any
        Offset for pagination
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
            "name": "NobelPrize_get_laureates",
            "arguments": {
                "name": name,
                "nobelPrizeYear": nobelPrizeYear,
                "nobelPrizeCategory": nobelPrizeCategory,
                "gender": gender,
                "birthCountry": birthCountry,
                "sort": sort,
                "limit": limit,
                "offset": offset,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NobelPrize_get_laureates"]
