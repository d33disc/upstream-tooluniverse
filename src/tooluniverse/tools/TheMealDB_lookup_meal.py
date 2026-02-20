"""
TheMealDB_lookup_meal

Look up the full details of a specific meal by its ID from TheMealDB. Returns the complete recipe...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheMealDB_lookup_meal(
    i: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up the full details of a specific meal by its ID from TheMealDB. Returns the complete recipe...

    Parameters
    ----------
    i : str
        Meal ID to look up. Examples: '52772' (Teriyaki Chicken Casserole), '52940' (...
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
        {"name": "TheMealDB_lookup_meal", "arguments": {"i": i}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheMealDB_lookup_meal"]
