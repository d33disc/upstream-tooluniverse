"""
LibraryOfCongress_search

Search the Library of Congress digital collections containing 21M+ historical items including pho...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def LibraryOfCongress_search(
    q: str,
    fa: Optional[str | Any] = None,
    dates: Optional[str | Any] = None,
    c: Optional[int | Any] = None,
    sp: Optional[int | Any] = None,
    fo: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Library of Congress digital collections containing 21M+ historical items including pho...

    Parameters
    ----------
    q : str
        Search query. Examples: 'Wright brothers airplane', 'Abraham Lincoln', 'Civil...
    fa : str | Any
        Facet filter. Format: 'field:value'. Examples: 'subject:science', 'date:1900/...
    dates : str | Any
        Date range filter (YYYY/YYYY format). Example: '1900/1950' for 1900-1950
    c : int | Any
        Number of results per page (default 25, max 150)
    sp : int | Any
        Start page for pagination
    fo : str | Any
        Format type filter. Examples: 'online', 'digitized'
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
            "name": "LibraryOfCongress_search",
            "arguments": {"q": q, "fa": fa, "dates": dates, "c": c, "sp": sp, "fo": fo},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LibraryOfCongress_search"]
