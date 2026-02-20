"""
PoetryDB_search_by_author

Search and retrieve poems by author from PoetryDB - a free poetry database with works from 129 cl...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PoetryDB_search_by_author(
    author: str,
    output_fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search and retrieve poems by author from PoetryDB - a free poetry database with works from 129 cl...

    Parameters
    ----------
    author : str
        Author name (full or partial). Examples: 'William Shakespeare', 'Emily Dickin...
    output_fields : str | Any
        Fields to return, comma-separated. Values: 'title', 'author', 'lines', 'linec...
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
            "name": "PoetryDB_search_by_author",
            "arguments": {"author": author, "output_fields": output_fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PoetryDB_search_by_author"]
