"""
PokeAPI_get_pokemon

Get detailed information about a Pokemon by name or ID using the PokeAPI. Returns stats, types, a...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokeAPI_get_pokemon(
    pokemon: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a Pokemon by name or ID using the PokeAPI. Returns stats, types, a...

    Parameters
    ----------
    pokemon : str
        Pokemon name (lowercase) or national Pokedex ID. Examples: 'pikachu', 'chariz...
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
        {"name": "PokeAPI_get_pokemon", "arguments": {"pokemon": pokemon}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PokeAPI_get_pokemon"]
