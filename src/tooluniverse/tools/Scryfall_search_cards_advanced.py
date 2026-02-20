"""
Scryfall_search_cards_advanced

Search Magic: The Gathering cards with advanced Scryfall syntax using the Scryfall API. Supports ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Scryfall_search_cards_advanced(
    q: str,
    order: Optional[str | Any] = None,
    unique: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Magic: The Gathering cards with advanced Scryfall syntax using the Scryfall API. Supports ...

    Parameters
    ----------
    q : str
        Scryfall search query. Examples: 'type:legendary+creature', 'oracle:"draw a c...
    order : str | Any
        Sort order. Values: 'name', 'set', 'released', 'rarity', 'color', 'usd', 'tix...
    unique : str | Any
        Uniqueness strategy. Values: 'cards' (one per name), 'art' (one per artwork),...
    page : int | Any
        Page number (175 cards per page). Default: 1
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
            "name": "Scryfall_search_cards_advanced",
            "arguments": {"q": q, "order": order, "unique": unique, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Scryfall_search_cards_advanced"]
