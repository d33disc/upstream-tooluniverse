"""
SpaceflightNews_search_articles

Search spaceflight news articles from 30,000+ stories across major space news sites (SpaceNews, N...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SpaceflightNews_search_articles(
    title_contains: Optional[str | Any] = None,
    summary_contains: Optional[str | Any] = None,
    news_site: Optional[str | Any] = None,
    published_at_gte: Optional[str | Any] = None,
    published_at_lte: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search spaceflight news articles from 30,000+ stories across major space news sites (SpaceNews, N...

    Parameters
    ----------
    title_contains : str | Any
        Filter articles containing this text in the title. Examples: 'Starship', 'Art...
    summary_contains : str | Any
        Filter articles containing this text in the summary
    news_site : str | Any
        Filter by news site name. Examples: 'NASA', 'SpaceNews', 'NASASpaceflight', '...
    published_at_gte : str | Any
        Filter articles published on or after this date (ISO 8601). Example: '2024-01...
    published_at_lte : str | Any
        Filter articles published on or before this date (ISO 8601). Example: '2024-1...
    limit : int | Any
        Number of articles to return (default 10, max 100)
    offset : int | Any
        Pagination offset
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
            "name": "SpaceflightNews_search_articles",
            "arguments": {
                "title_contains": title_contains,
                "summary_contains": summary_contains,
                "news_site": news_site,
                "published_at_gte": published_at_gte,
                "published_at_lte": published_at_lte,
                "limit": limit,
                "offset": offset,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SpaceflightNews_search_articles"]
