"""
TheCocktailDB_search_ingredient

Search for ingredient details in TheCocktailDB by name. Returns the ingredient's description, typ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCocktailDB_search_ingredient(
    i: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for ingredient details in TheCocktailDB by name. Returns the ingredient's description, typ...

    Parameters
    ----------
    i : str
        Ingredient name to look up. Examples: 'vodka', 'gin', 'rum', 'tequila', 'trip...
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
        {"name": "TheCocktailDB_search_ingredient", "arguments": {"i": i}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCocktailDB_search_ingredient"]
