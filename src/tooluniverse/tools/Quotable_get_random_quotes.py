"""
Quotable_get_random_quotes

Get random inspirational quotes using the Quotable API. Can filter by author, tags (philosophy, s...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Quotable_get_random_quotes(
    limit: Optional[int | Any] = None,
    tags: Optional[str | Any] = None,
    author: Optional[str | Any] = None,
    minLength: Optional[int | Any] = None,
    maxLength: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get random inspirational quotes using the Quotable API. Can filter by author, tags (philosophy, s...

    Parameters
    ----------
    limit : int | Any
        Number of random quotes to return (1-150). Default: 1
    tags : str | Any
        Filter by tags (pipe-separated for OR, comma-separated for AND). Examples: 's...
    author : str | Any
        Filter by author slug. Examples: 'albert-einstein', 'mark-twain', 'winston-ch...
    minLength : int | Any
        Minimum quote character length
    maxLength : int | Any
        Maximum quote character length. Use 100 for short quotes
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
            "name": "Quotable_get_random_quotes",
            "arguments": {
                "limit": limit,
                "tags": tags,
                "author": author,
                "minLength": minLength,
                "maxLength": maxLength,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Quotable_get_random_quotes"]
