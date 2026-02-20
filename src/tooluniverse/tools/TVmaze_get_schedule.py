"""
TVmaze_get_schedule

Get TV show schedule for a specific date and country using the TVmaze API. Returns list of episod...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TVmaze_get_schedule(
    date: Optional[str | Any] = None,
    country: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get TV show schedule for a specific date and country using the TVmaze API. Returns list of episod...

    Parameters
    ----------
    date : str | Any
        Date in YYYY-MM-DD format. Default: today. Examples: '2024-01-15', '2025-03-01'
    country : str | Any
        ISO 3166-1 country code. Default: US. Examples: 'US', 'GB', 'AU', 'CA', 'DE'
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
            "name": "TVmaze_get_schedule",
            "arguments": {"date": date, "country": country},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TVmaze_get_schedule"]
