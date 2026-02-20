"""
CheapShark_search_game_deals

Search for video game deals and discounts from multiple online stores (Steam, Epic, GOG, Humble, ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CheapShark_search_game_deals(
    title: Optional[str | Any] = None,
    sortBy: Optional[str | Any] = None,
    pageSize: Optional[int | Any] = None,
    upperPrice: Optional[float | Any] = None,
    metacritic: Optional[int | Any] = None,
    onSale: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for video game deals and discounts from multiple online stores (Steam, Epic, GOG, Humble, ...

    Parameters
    ----------
    title : str | Any
        Game title to search for. Examples: 'cyberpunk', 'witcher', 'doom eternal', '...
    sortBy : str | Any
        Sort order. Values: 'DealRating' (default), 'Title', 'Savings', 'Price', 'Met...
    pageSize : int | Any
        Results per page (1-60). Default: 10
    upperPrice : float | Any
        Maximum price filter in USD. Example: 15.00 for games under $15
    metacritic : int | Any
        Minimum Metacritic score filter (0-100). Example: 80 for highly-rated games
    onSale : int | Any
        Filter to only on-sale games. Values: 1 (only sales), 0 (all). Default: 0
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
            "name": "CheapShark_search_game_deals",
            "arguments": {
                "title": title,
                "sortBy": sortBy,
                "pageSize": pageSize,
                "upperPrice": upperPrice,
                "metacritic": metacritic,
                "onSale": onSale,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CheapShark_search_game_deals"]
