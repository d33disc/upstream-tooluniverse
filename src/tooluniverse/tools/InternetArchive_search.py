"""
InternetArchive_search

Search the Internet Archive's collection of 40M+ items including books, movies, audio, software, ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def InternetArchive_search(
    q: str,
    rows: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    fl: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Internet Archive's collection of 40M+ items including books, movies, audio, software, ...

    Parameters
    ----------
    q : str
        Search query. Free text or field-specific: 'subject:physics', 'creator:Shakes...
    rows : int | Any
        Number of results to return (default 10, max 10000)
    page : int | Any
        Page number for pagination (default 1)
    fl : str | Any
        Comma-separated list of fields to return (default: 'identifier,title,creator,...
    sort : str | Any
        Sort field and direction (e.g., 'downloads desc', 'date asc', 'title asc', 'a...
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
            "name": "InternetArchive_search",
            "arguments": {"q": q, "rows": rows, "page": page, "fl": fl, "sort": sort},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["InternetArchive_search"]
