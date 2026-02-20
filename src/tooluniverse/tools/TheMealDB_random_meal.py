"""
TheMealDB_random_meal

Get a random meal recipe from TheMealDB. Returns a complete random meal with all ingredients, mea...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheMealDB_random_meal(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random meal recipe from TheMealDB. Returns a complete random meal with all ingredients, mea...

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
        {"name": "TheMealDB_random_meal", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheMealDB_random_meal"]
