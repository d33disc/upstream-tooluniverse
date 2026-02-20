"""
DeckOfCards_draw_cards

Draw one or more cards from an existing deck using the Deck of Cards API. Requires a deck_id from...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DeckOfCards_draw_cards(
    deck_id: str,
    count: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Draw one or more cards from an existing deck using the Deck of Cards API. Requires a deck_id from...

    Parameters
    ----------
    deck_id : str
        The deck identifier from DeckOfCards_new_deck. Example: '3p40paa87x90'
    count : int | Any
        Number of cards to draw (default 1). Cannot exceed remaining cards in the deck.
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
            "name": "DeckOfCards_draw_cards",
            "arguments": {"deck_id": deck_id, "count": count},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DeckOfCards_draw_cards"]
