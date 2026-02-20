"""
ChroniclingAmerica_search_newspapers

Search historic US newspaper pages from the Library of Congress Chronicling America collection. C...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ChroniclingAmerica_search_newspapers(
    q: str,
    dates: Optional[str | Any] = None,
    c: Optional[int | Any] = None,
    sp: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search historic US newspaper pages from the Library of Congress Chronicling America collection. C...

    Parameters
    ----------
    q : str
        Search query for full-text search of newspaper content. Supports AND/OR/NOT a...
    dates : str | Any
        Year or year range to filter results. Examples: '1863' (single year), '1900/1...
    c : int | Any
        Number of results per page (default 20, max 160). Each result is one newspape...
    sp : int | Any
        Page number for pagination (starts at 1).
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
            "name": "ChroniclingAmerica_search_newspapers",
            "arguments": {"q": q, "dates": dates, "c": c, "sp": sp},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ChroniclingAmerica_search_newspapers"]
