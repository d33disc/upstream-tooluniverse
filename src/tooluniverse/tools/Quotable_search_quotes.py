"""
Quotable_search_quotes

Search for quotes by keyword using the Quotable API. Returns paginated list of matching quotes wi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Quotable_search_quotes(
    query: str,
    limit: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for quotes by keyword using the Quotable API. Returns paginated list of matching quotes wi...

    Parameters
    ----------
    query : str
        Search query keyword(s) to find in quote text. Examples: 'imagination', 'cour...
    limit : int | Any
        Number of results per page (1-150). Default: 20
    page : int | Any
        Page number for pagination. Default: 1
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
            "name": "Quotable_search_quotes",
            "arguments": {"query": query, "limit": limit, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Quotable_search_quotes"]
