"""
PokeAPI_get_species

Get species-level biological information about a Pokemon from PokeAPI. Returns habitat, color, sh...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokeAPI_get_species(
    name_or_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get species-level biological information about a Pokemon from PokeAPI. Returns habitat, color, sh...

    Parameters
    ----------
    name_or_id : str
        Pokemon species name (lowercase) or Pokedex number. Examples: 'pikachu', 'eev...
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
        {"name": "PokeAPI_get_species", "arguments": {"name_or_id": name_or_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PokeAPI_get_species"]
