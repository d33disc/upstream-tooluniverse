"""
FakeStore_get_categories

Get all product categories from the Fake Store API. Returns the list of available categories: ele...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FakeStore_get_categories(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get all product categories from the Fake Store API. Returns the list of available categories: ele...

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
        {"name": "FakeStore_get_categories", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FakeStore_get_categories"]
