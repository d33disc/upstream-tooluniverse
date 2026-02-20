"""
TheCocktailDB_random_cocktail

Get a random cocktail recipe from TheCocktailDB. Returns a complete cocktail with all ingredients...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCocktailDB_random_cocktail(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random cocktail recipe from TheCocktailDB. Returns a complete cocktail with all ingredients...

    Parameters
    ----------
    No parameters
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
        {"name": "TheCocktailDB_random_cocktail", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCocktailDB_random_cocktail"]
