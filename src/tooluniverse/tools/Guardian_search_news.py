"""
Guardian_search_news

Search The Guardian newspaper for news articles by keyword, section, and date range. The Guardian...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Guardian_search_news(
    q: str,
    section: Optional[str | Any] = None,
    from_date: Optional[str | Any] = None,
    to_date: Optional[str | Any] = None,
    page_size: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    order_by: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search The Guardian newspaper for news articles by keyword, section, and date range. The Guardian...

    Parameters
    ----------
    q : str
        Search query keywords. Supports AND/OR/NOT operators and phrase search with q...
    section : str | Any
        Filter by Guardian section. Common sections: 'science', 'technology', 'enviro...
    from_date : str | Any
        Start date filter in YYYY-MM-DD format (e.g., '2025-01-01'). Returns articles...
    to_date : str | Any
        End date filter in YYYY-MM-DD format (e.g., '2025-12-31'). Returns articles p...
    page_size : int | Any
        Number of results per page (1-50, default 10). Use smaller values for quick l...
    page : int | Any
        Page number for pagination (starts at 1). Use with page-size to retrieve more...
    order_by : str | Any
        Sort order for results. Options: 'relevance' (default), 'newest', 'oldest'.
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
            "name": "Guardian_search_news",
            "arguments": {
                "q": q,
                "section": section,
                "from-date": from_date,
                "to-date": to_date,
                "page-size": page_size,
                "page": page,
                "order-by": order_by,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Guardian_search_news"]
