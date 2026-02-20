"""
TheMealDB_filter_meals

Filter meals from TheMealDB by main ingredient, category, or cuisine area. Returns an abbreviated...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheMealDB_filter_meals(
    i: Optional[str | Any] = None,
    c: Optional[str | Any] = None,
    a: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Filter meals from TheMealDB by main ingredient, category, or cuisine area. Returns an abbreviated...

    Parameters
    ----------
    i : str | Any
        Filter by main ingredient name. Examples: 'chicken_breast', 'salmon', 'rice',...
    c : str | Any
        Filter by category. Values: 'Beef', 'Chicken', 'Dessert', 'Lamb', 'Miscellane...
    a : str | Any
        Filter by cuisine area. Values: 'Italian', 'Japanese', 'Mexican', 'Indian', '...
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
        {"name": "TheMealDB_filter_meals", "arguments": {"i": i, "c": c, "a": a}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheMealDB_filter_meals"]
