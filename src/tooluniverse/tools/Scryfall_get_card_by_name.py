"""
Scryfall_get_card_by_name

Get a specific Magic: The Gathering card by exact or fuzzy name match using the Scryfall API. Ret...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Scryfall_get_card_by_name(
    exact: Optional[str | Any] = None,
    fuzzy: Optional[str | Any] = None,
    set: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a specific Magic: The Gathering card by exact or fuzzy name match using the Scryfall API. Ret...

    Parameters
    ----------
    exact : str | Any
        Exact card name (case-insensitive). Examples: 'Black Lotus', 'Lightning Bolt'...
    fuzzy : str | Any
        Fuzzy card name (best match). Examples: 'bolt', 'counter spell', 'black lotus'
    set : str | Any
        Set code to narrow the search. Examples: 'lea', 'm21', 'mh3'
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
            "name": "Scryfall_get_card_by_name",
            "arguments": {"exact": exact, "fuzzy": fuzzy, "set": set},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Scryfall_get_card_by_name"]
