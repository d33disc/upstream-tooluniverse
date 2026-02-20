"""
TheCocktailDB_filter_cocktails

Filter cocktails by ingredient, category, glass type, or alcoholic content in TheCocktailDB. Retu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCocktailDB_filter_cocktails(
    i: Optional[str | Any] = None,
    c: Optional[str | Any] = None,
    g: Optional[str | Any] = None,
    a: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Filter cocktails by ingredient, category, glass type, or alcoholic content in TheCocktailDB. Retu...

    Parameters
    ----------
    i : str | Any
        Filter by ingredient name. Examples: 'Vodka', 'Gin', 'Rum', 'Tequila', 'Whisk...
    c : str | Any
        Filter by category. Values: 'Ordinary Drink', 'Cocktail', 'Milk / Float / Sha...
    g : str | Any
        Filter by glass type. Examples: 'Cocktail glass', 'Highball glass', 'Old-fash...
    a : str | Any
        Filter by alcoholic content. Values: 'Alcoholic', 'Non_Alcoholic', 'Optional_...
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
        {
            "name": "TheCocktailDB_filter_cocktails",
            "arguments": {"i": i, "c": c, "g": g, "a": a},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCocktailDB_filter_cocktails"]
