"""
TheCocktailDB_search_cocktails

Search for cocktail recipes by name in TheCocktailDB, a comprehensive free cocktail database. Ret...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCocktailDB_search_cocktails(
    s: Optional[str | Any] = None,
    f: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for cocktail recipes by name in TheCocktailDB, a comprehensive free cocktail database. Ret...

    Parameters
    ----------
    s : str | Any
        Search by cocktail name. Examples: 'margarita', 'mojito', 'martini', 'negroni...
    f : str | Any
        Search by first letter of cocktail name. Single character: 'a', 'b', 'm', etc.
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
        {"name": "TheCocktailDB_search_cocktails", "arguments": {"s": s, "f": f}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCocktailDB_search_cocktails"]
