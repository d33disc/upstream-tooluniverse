"""
YuGiOh_search_cards

Search for Yu-Gi-Oh! trading card game cards using the YGOPRODeck API. Supports fuzzy name matchi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def YuGiOh_search_cards(
    fname: Optional[str | Any] = None,
    name: Optional[str | Any] = None,
    type_: Optional[str | Any] = None,
    attribute: Optional[str | Any] = None,
    race: Optional[str | Any] = None,
    archetype: Optional[str | Any] = None,
    level: Optional[int | Any] = None,
    atk: Optional[int | Any] = None,
    def_: Optional[int | Any] = None,
    num: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for Yu-Gi-Oh! trading card game cards using the YGOPRODeck API. Supports fuzzy name matchi...

    Parameters
    ----------
    fname : str | Any
        Fuzzy card name search (partial match). Examples: 'dragon', 'dark magician', ...
    name : str | Any
        Exact card name. Examples: 'Blue-Eyes White Dragon', 'Dark Magician', 'Pot of...
    type_ : str | Any
        Card type filter. Values: 'Normal Monster', 'Effect Monster', 'Fusion Monster...
    attribute : str | Any
        Monster attribute. Values: 'DARK', 'LIGHT', 'EARTH', 'WATER', 'FIRE', 'WIND',...
    race : str | Any
        Monster race/subtype. Examples: 'Dragon', 'Spellcaster', 'Warrior', 'Machine'...
    archetype : str | Any
        Card archetype. Examples: 'Blue-Eyes', 'Dark Magician', 'HERO', 'Exodia', 'Cy...
    level : int | Any
        Monster level/rank (1-12). Example: 8 for Level 8 monsters
    atk : int | Any
        Exact ATK value. Example: 3000
    def_ : int | Any
        Exact DEF value. Example: 2500
    num : int | Any
        Number of results to return. Default: 20
    offset : int | Any
        Offset for pagination. Default: 0
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
            "name": "YuGiOh_search_cards",
            "arguments": {
                "fname": fname,
                "name": name,
                "type": type_,
                "attribute": attribute,
                "race": race,
                "archetype": archetype,
                "level": level,
                "atk": atk,
                "def": def_,
                "num": num,
                "offset": offset,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["YuGiOh_search_cards"]
