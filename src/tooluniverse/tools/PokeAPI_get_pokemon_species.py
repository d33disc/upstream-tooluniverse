"""
PokeAPI_get_pokemon_species

Get species-level information about a Pokemon from the PokeAPI, including flavor text (Pokedex en...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokeAPI_get_pokemon_species(
    species: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get species-level information about a Pokemon from the PokeAPI, including flavor text (Pokedex en...

    Parameters
    ----------
    species : str
        Pokemon species name (lowercase) or ID. Examples: 'pikachu', 'eevee', 'mew', ...
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
        {"name": "PokeAPI_get_pokemon_species", "arguments": {"species": species}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PokeAPI_get_pokemon_species"]
