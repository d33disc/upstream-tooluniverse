"""
PokemonTCG_get_card

Get detailed information about a specific Pokemon TCG card by its unique ID. Returns comprehensiv...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokemonTCG_get_card(
    card_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific Pokemon TCG card by its unique ID. Returns comprehensiv...

    Parameters
    ----------
    card_id : str
        Unique card ID in format 'setId-number'. Examples: 'base1-4' (Charizard Base ...
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
        {"name": "PokemonTCG_get_card", "arguments": {"card_id": card_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PokemonTCG_get_card"]
