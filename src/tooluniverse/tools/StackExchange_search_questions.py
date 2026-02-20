"""
StackExchange_search_questions

Search for questions on StackOverflow or other StackExchange sites. Returns questions matching a ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def StackExchange_search_questions(
    q: str,
    site: Optional[str | Any] = None,
    sort: Optional[str | Any] = None,
    order: Optional[str | Any] = None,
    tagged: Optional[str | Any] = None,
    pagesize: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for questions on StackOverflow or other StackExchange sites. Returns questions matching a ...

    Parameters
    ----------
    q : str
        Search query string (e.g., 'python pandas dataframe merge')
    site : str | Any
        StackExchange site to search (default: 'stackoverflow'). Other options: 'serv...
    sort : str | Any
        Sort order: 'relevance', 'votes', 'creation', 'activity' (default: 'relevance')
    order : str | Any
        Sort direction: 'desc' or 'asc' (default: 'desc')
    tagged : str | Any
        Semicolon-separated tags to filter by (e.g., 'python;pandas')
    pagesize : int | Any
        Number of results per page (1-100, default: 10)
    page : int | Any
        Page number for pagination (default: 1)
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
                "q": q,
                "site": site,
                "sort": sort,
                "order": order,
                "tagged": tagged,
                "pagesize": pagesize,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["StackExchange_search_questions"]
