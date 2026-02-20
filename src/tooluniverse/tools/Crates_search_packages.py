"""
Crates_search_packages

Search for Rust crates (packages) on crates.io, the Rust package registry. Returns matching crate...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Crates_search_packages(
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
    Search for Rust crates (packages) on crates.io, the Rust package registry. Returns matching crate...

    Parameters
    ----------
    q : str
        Search query string (e.g., 'serde', 'async runtime', 'web framework', 'cli pa...
    per_page : int | Any
        Number of results per page (default 10, max 100)
    page : int | Any
        Page number for pagination (default 1)
    sort : str | Any
        Sort order: 'relevance' (default), 'downloads', 'recent-downloads', 'recent-u...
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
            "name": "Crates_search_packages",
            "arguments": {"q": q, "per_page": per_page, "page": page, "sort": sort},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Crates_search_packages"]
