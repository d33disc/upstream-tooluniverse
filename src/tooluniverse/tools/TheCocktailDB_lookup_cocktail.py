"""
TheCocktailDB_lookup_cocktail

Look up full details of a specific cocktail by its ID in TheCocktailDB. Returns complete recipe i...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCocktailDB_lookup_cocktail(
    i: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up full details of a specific cocktail by its ID in TheCocktailDB. Returns complete recipe i...

    Parameters
    ----------
    i : str
        Cocktail ID. Examples: '11007' (Margarita), '11000' (Mojito), '11001' (Old Fa...
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
        {"name": "TheCocktailDB_lookup_cocktail", "arguments": {"i": i}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCocktailDB_lookup_cocktail"]
