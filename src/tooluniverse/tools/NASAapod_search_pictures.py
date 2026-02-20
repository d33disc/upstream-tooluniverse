"""
NASAapod_search_pictures

Get NASA Astronomy Picture of the Day (APOD) entries for a date range. Returns an array of APOD e...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASAapod_search_pictures(
    start_date: str,
    end_date: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get NASA Astronomy Picture of the Day (APOD) entries for a date range. Returns an array of APOD e...

    Parameters
    ----------
    start_date : str
        Start date in YYYY-MM-DD format (e.g., '2024-01-01'). Must be 1995-06-16 or l...
    end_date : str
        End date in YYYY-MM-DD format (e.g., '2024-01-07'). Must be no later than today.
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
            "name": "NASAapod_search_pictures",
            "arguments": {"start_date": start_date, "end_date": end_date},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASAapod_search_pictures"]
