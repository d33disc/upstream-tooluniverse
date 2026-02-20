"""
FakeStore_get_products

Get products from the Fake Store API, a free online REST API for e-commerce prototyping and testi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FakeStore_get_products(
    limit: Optional[int | Any] = None,
    sort: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get products from the Fake Store API, a free online REST API for e-commerce prototyping and testi...

    Parameters
    ----------
    limit : int | Any
        Limit number of products returned (1-20). Omit for all products.
    sort : str | Any
        Sort order: 'asc' (ascending) or 'desc' (descending). Default: ascending.
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
        {"name": "FakeStore_get_products", "arguments": {"limit": limit, "sort": sort}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FakeStore_get_products"]
