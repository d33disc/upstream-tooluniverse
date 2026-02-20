"""
PokeAPI_get_pokemon

Get detailed information about a Pokemon species from PokeAPI. Returns base stats (HP, Attack, De...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PokeAPI_get_pokemon(
    name_or_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a Pokemon species from PokeAPI. Returns base stats (HP, Attack, De...

    Parameters
    ----------
    name_or_id : str
        Pokemon name (lowercase, use hyphens for spaces) or Pokedex number. Examples:...
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
        {"name": "PokeAPI_get_pokemon", "arguments": {"name_or_id": name_or_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PokeAPI_get_pokemon"]
