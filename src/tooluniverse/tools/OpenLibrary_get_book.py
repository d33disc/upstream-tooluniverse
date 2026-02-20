"""
OpenLibrary_get_book

Get detailed metadata for a specific book from Open Library by its ISBN or Open Library ID. Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLibrary_get_book(
    bibkeys: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed metadata for a specific book from Open Library by its ISBN or Open Library ID. Retur...

    Parameters
    ----------
    bibkeys : str
        Book identifier(s). Use 'ISBN:' prefix for ISBN-10 or ISBN-13 (e.g., 'ISBN:97...
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
        {"name": "OpenLibrary_get_book", "arguments": {"bibkeys": bibkeys}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLibrary_get_book"]
