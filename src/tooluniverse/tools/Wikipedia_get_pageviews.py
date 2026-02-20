"""
Wikipedia_get_pageviews

Get Wikipedia page view statistics for a specific article using the Wikimedia REST API. Returns d...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Wikipedia_get_pageviews(
    article: str,
    start: str,
    end: str,
    project: Optional[str | Any] = None,
    access: Optional[str | Any] = None,
    agent: Optional[str | Any] = None,
    granularity: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Wikipedia page view statistics for a specific article using the Wikimedia REST API. Returns d...

    Parameters
    ----------
    article : str
        Wikipedia article title (use underscores for spaces). Examples: 'CRISPR', 'Al...
    project : str | Any
        Wikipedia language project. Default: 'en.wikipedia'. Examples: 'en.wikipedia'...
    access : str | Any
        Access type filter. Values: 'all-access' (default), 'desktop', 'mobile-app', ...
    agent : str | Any
        Agent type filter. Values: 'all-agents' (default), 'user', 'bot', 'spider'
    granularity : str | Any
        Time granularity: 'daily' or 'monthly'. Default: 'monthly'
    start : str
        Start date (YYYYMMDD or YYYYMM format). Example: '20240101' for Jan 1 2024, '...
    end : str
        End date (YYYYMMDD or YYYYMM format). Example: '20240201' for Feb 1 2024, '20...
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
            "name": "Wikipedia_get_pageviews",
            "arguments": {
                "article": article,
                "project": project,
                "access": access,
                "agent": agent,
                "granularity": granularity,
                "start": start,
                "end": end,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Wikipedia_get_pageviews"]
