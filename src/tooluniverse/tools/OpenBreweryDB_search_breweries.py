"""
OpenBreweryDB_search_breweries

Search for breweries by city, state, country, type, or name using the Open Brewery DB API. Return...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenBreweryDB_search_breweries(
    by_city: Optional[str | Any] = None,
    by_state: Optional[str | Any] = None,
    by_country: Optional[str | Any] = None,
    by_name: Optional[str | Any] = None,
    by_type: Optional[str | Any] = None,
    per_page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for breweries by city, state, country, type, or name using the Open Brewery DB API. Return...

    Parameters
    ----------
    by_city : str | Any
        Filter by city name. Examples: 'seattle', 'portland', 'denver', 'london'
    by_state : str | Any
        Filter by US state (full name or abbreviation). Examples: 'california', 'new ...
    by_country : str | Any
        Filter by country. Examples: 'united_states', 'england', 'south_korea'
    by_name : str | Any
        Filter by brewery name. Examples: 'dog', 'sierra', 'stone'
    by_type : str | Any
        Filter by brewery type. Values: 'micro', 'nano', 'regional', 'brewpub', 'larg...
    per_page : int | Any
        Number of results per page (max 200). Default: 50
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
            "name": "OpenBreweryDB_search_breweries",
            "arguments": {
                "by_city": by_city,
                "by_state": by_state,
                "by_country": by_country,
                "by_name": by_name,
                "by_type": by_type,
                "per_page": per_page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenBreweryDB_search_breweries"]
