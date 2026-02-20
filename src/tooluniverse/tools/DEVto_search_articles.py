"""
DEVto_search_articles

Search and browse developer articles from DEV.to (dev.to), a community of software developers sha...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DEVto_search_articles(
    tag: Optional[str | Any] = None,
    top: Optional[int | Any] = None,
    per_page: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search and browse developer articles from DEV.to (dev.to), a community of software developers sha...

    Parameters
    ----------
    tag : str | Any
        Filter by tag. Examples: 'python', 'javascript', 'rust', 'webdev', 'beginners...
    top : int | Any
        Return top articles from last N days. Examples: 7 (week), 30 (month), 365 (ye...
    per_page : int | Any
        Number of articles to return (1-30). Default: 10
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
            "name": "DEVto_search_articles",
            "arguments": {"tag": tag, "top": top, "per_page": per_page, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DEVto_search_articles"]
