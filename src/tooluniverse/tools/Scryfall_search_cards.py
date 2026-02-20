"""
Scryfall_search_cards

Search Magic: The Gathering cards using the Scryfall API with powerful query syntax. Returns card...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Scryfall_search_cards(
    q: str,
    order: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Magic: The Gathering cards using the Scryfall API with powerful query syntax. Returns card...

    Parameters
    ----------
    q : str
        Scryfall search query. Examples: 'oracle:fly type:creature' (flying creatures...
    order : str | Any
        Sort order. Values: 'name', 'set', 'released', 'rarity', 'color', 'usd', 'eur...
    page : int | Any
        Page number (175 cards per page)
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
            "name": "Scryfall_search_cards",
            "arguments": {"q": q, "order": order, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Scryfall_search_cards"]
