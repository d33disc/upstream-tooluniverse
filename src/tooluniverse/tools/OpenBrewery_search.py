"""
OpenBrewery_search

Search breweries in the Open Brewery DB - a free database of 8,000+ breweries, cideries, bottlesh...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenBrewery_search(
    by_name: Optional[str | Any] = None,
    by_city: Optional[str | Any] = None,
    by_state: Optional[str | Any] = None,
    by_country: Optional[str | Any] = None,
    by_type: Optional[str | Any] = None,
    by_postal: Optional[str | Any] = None,
    by_dist: Optional[str | Any] = None,
    per_page: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    sort: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search breweries in the Open Brewery DB - a free database of 8,000+ breweries, cideries, bottlesh...

    Parameters
    ----------
    by_name : str | Any
        Filter by brewery name (partial match). Example: 'dogfish head'
    by_city : str | Any
        Filter by city name. Example: 'san francisco', 'denver', 'portland'
    by_state : str | Any
        Filter by state/province. Use full name (US). Example: 'california', 'new yor...
    by_country : str | Any
        Filter by country. Example: 'united states', 'united kingdom', 'germany'
    by_type : str | Any
        Filter by brewery type. Values: 'micro' (small independent), 'nano' (very sma...
    by_postal : str | Any
        Filter by postal/zip code. Example: '94107', 'EC2A 4BX'
    by_dist : str | Any
        Sort by distance from coordinates. Format: 'latitude,longitude'. Example: '37...
    per_page : int | Any
        Number of results per page (default 20, max 200)
    page : int | Any
        Page number for pagination (default 1)
    sort : str | Any
        Sort field and direction. Format: 'field:asc' or 'field:desc'. Example: 'name...
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
            "name": "OpenBrewery_search",
            "arguments": {
                "by_name": by_name,
                "by_city": by_city,
                "by_state": by_state,
                "by_country": by_country,
                "by_type": by_type,
                "by_postal": by_postal,
                "by_dist": by_dist,
                "per_page": per_page,
                "page": page,
                "sort": sort,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenBrewery_search"]
