"""
NASANeoWs_get_feed

Get a list of near-Earth asteroids (NEOs) approaching Earth within a date range using NASA's NeoW...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASANeoWs_get_feed(
    start_date: str,
    end_date: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a list of near-Earth asteroids (NEOs) approaching Earth within a date range using NASA's NeoW...

    Parameters
    ----------
    start_date : str
        Start date in YYYY-MM-DD format (e.g., '2025-01-15'). Feed covers up to 7 day...
    end_date : str | Any
        End date in YYYY-MM-DD format (e.g., '2025-01-16'). Must be within 7 days of ...
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
            "name": "NASANeoWs_get_feed",
            "arguments": {"start_date": start_date, "end_date": end_date},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASANeoWs_get_feed"]
