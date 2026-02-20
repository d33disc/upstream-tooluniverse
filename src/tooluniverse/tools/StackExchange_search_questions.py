"""
StackExchange_search_questions

Search for questions on Stack Exchange sites (Stack Overflow, Super User, Server Fault, etc.) usi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def StackExchange_search_questions(
    intitle: Optional[str | Any] = None,
    tagged: Optional[str | Any] = None,
    site: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    order: Optional[str | Any] = None,
    pagesize: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for questions on Stack Exchange sites (Stack Overflow, Super User, Server Fault, etc.) usi...

    Parameters
    ----------
    intitle : str | Any
        Search query to find in question titles. Examples: 'python list comprehension...
    tagged : str | Any
        Semicolon-separated tags to filter by. Examples: 'python', 'javascript;react'...
    site : str | Any
        Stack Exchange site. Default: stackoverflow. Examples: 'stackoverflow', 'supe...
    sort : str | Any
        Sort order. Values: 'activity', 'votes', 'creation', 'relevance'. Default: 'a...
    order : str | Any
        Order direction. Values: 'desc', 'asc'. Default: 'desc'
    pagesize : int | Any
        Number of results per page (1-100). Default: 10
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
            "name": "StackExchange_search_questions",
            "arguments": {
                "intitle": intitle,
                "tagged": tagged,
                "site": site,
                "sort": sort,
                "order": order,
                "pagesize": pagesize,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["StackExchange_search_questions"]
