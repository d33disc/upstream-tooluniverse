"""
Wikipedia_get_top_pages

Get the most viewed Wikipedia articles for a specific date using the Wikimedia REST API. Returns ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Wikipedia_get_top_pages(
    year: str,
    month: str,
    day: str,
    project: Optional[str | Any] = None,
    access: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the most viewed Wikipedia articles for a specific date using the Wikimedia REST API. Returns ...

    Parameters
    ----------
    project : str | Any
        Wikipedia language project. Default: 'en.wikipedia'. Examples: 'en.wikipedia'...
    access : str | Any
        Access type. Values: 'all-access' (default), 'desktop', 'mobile-app', 'mobile...
    year : str
        Year (4 digits). Example: '2024'
    month : str
        Month (2 digits, zero-padded). Example: '01' for January
    day : str
        Day (2 digits, zero-padded). Example: '15'. Use 'all-days' for monthly totals.
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
            "name": "Wikipedia_get_top_pages",
            "arguments": {
                "project": project,
                "access": access,
                "year": year,
                "month": month,
                "day": day,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Wikipedia_get_top_pages"]
