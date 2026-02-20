"""
NASAapod_get_picture

Get NASA's Astronomy Picture of the Day (APOD) for a specific date or random entries. APOD has fe...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASAapod_get_picture(
    date: Optional[str | Any] = None,
    count: Optional[int | Any] = None,
    start_date: Optional[str | Any] = None,
    end_date: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get NASA's Astronomy Picture of the Day (APOD) for a specific date or random entries. APOD has fe...

    Parameters
    ----------
    date : str | Any
        Date of the APOD image in YYYY-MM-DD format (e.g., '2024-01-01'). Dates range...
    count : int | Any
        Number of random APOD entries to return (1-100). Cannot be used with date or ...
    start_date : str | Any
        Start date for a date range query in YYYY-MM-DD format. Must be used with end...
    end_date : str | Any
        End date for a date range query in YYYY-MM-DD format. Must be used with start...
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
            "name": "NASAapod_get_picture",
            "arguments": {
                "date": date,
                "count": count,
                "start_date": start_date,
                "end_date": end_date,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASAapod_get_picture"]
