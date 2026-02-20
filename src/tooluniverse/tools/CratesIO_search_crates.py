"""
CratesIO_search_crates

Search for Rust crates (packages) on crates.io, the official Rust package registry. Returns crate...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CratesIO_search_crates(
    q: str,
    per_page: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    sort: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for Rust crates (packages) on crates.io, the official Rust package registry. Returns crate...

    Parameters
    ----------
    q : str
        Search query for crate name or description. Examples: 'serde', 'web framework...
    per_page : int | Any
        Results per page (1-100). Default: 10
    page : int | Any
        Page number. Default: 1
    sort : str | Any
        Sort order. Values: 'relevance' (default), 'downloads', 'recent-downloads', '...
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
            "name": "CratesIO_search_crates",
            "arguments": {"q": q, "per_page": per_page, "page": page, "sort": sort},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CratesIO_search_crates"]
