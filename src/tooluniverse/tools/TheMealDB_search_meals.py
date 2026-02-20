"""
TheMealDB_search_meals

Search for meal recipes in TheMealDB, a free food recipe database with 300+ international recipes...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheMealDB_search_meals(
    s: Optional[str | Any] = None,
    c: Optional[str | Any] = None,
    a: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for meal recipes in TheMealDB, a free food recipe database with 300+ international recipes...

    Parameters
    ----------
    s : str | Any
        Search by meal name. Examples: 'chicken', 'pasta', 'sushi', 'beef stew', 'cho...
    c : str | Any
        Filter by category. Values: 'Beef', 'Chicken', 'Dessert', 'Lamb', 'Miscellane...
    a : str | Any
        Filter by cuisine area. Examples: 'Italian', 'Japanese', 'Mexican', 'Indian',...
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
        {"name": "TheMealDB_search_meals", "arguments": {"s": s, "c": c, "a": a}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheMealDB_search_meals"]
