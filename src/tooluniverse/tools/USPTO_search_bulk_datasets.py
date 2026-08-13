"""
USPTO_search_bulk_datasets

Search the USPTO Bulk Data Storage System (BDSS) product catalog. Returns available bulk dataset ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def USPTO_search_bulk_datasets(
    q: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Search the USPTO Bulk Data Storage System (BDSS) product catalog. Returns available bulk dataset ...

    Parameters
    ----------
    q : str
        Search query, e.g. 'patent'.
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    # Strip None values so optional parameters don't trigger schema validation errors
    _args = {k: v for k, v in {"q": q}.items() if v is not None}
    return get_shared_client().run_one_function(
        {
            "name": "USPTO_search_bulk_datasets",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["USPTO_search_bulk_datasets"]
