"""
Scryfall_get_random_card

Get a random Magic: The Gathering card from Scryfall. Optionally filter with a query to get a ran...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Scryfall_get_random_card(
    q: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random Magic: The Gathering card from Scryfall. Optionally filter with a query to get a ran...

    Parameters
    ----------
    q : str | Any
        Optional filter query for the random card. Examples: 'type:dragon', 'color:r ...
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
        {"name": "Scryfall_get_random_card", "arguments": {"q": q}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Scryfall_get_random_card"]
