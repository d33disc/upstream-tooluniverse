"""
DeckOfCards_new_deck

Create and shuffle a new deck of playing cards using the Deck of Cards API. Returns a deck_id tha...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DeckOfCards_new_deck(
    deck_count: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Create and shuffle a new deck of playing cards using the Deck of Cards API. Returns a deck_id tha...

    Parameters
    ----------
    deck_count : int | Any
        Number of decks to shuffle together (default 1, max 20). Use multiple decks f...
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
        {"name": "DeckOfCards_new_deck", "arguments": {"deck_count": deck_count}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DeckOfCards_new_deck"]
