"""
PublicHolidays_check_is_holiday

Check if a specific date is a public holiday in a given country using the Nager.Date API. Returns...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PublicHolidays_check_is_holiday(
    date: str,
    countryCode: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Check if a specific date is a public holiday in a given country using the Nager.Date API. Returns...

    Parameters
    ----------
    date : str
        Date to check in ISO format (YYYY-MM-DD). Examples: '2024-12-25', '2024-07-04...
    countryCode : str
        ISO 3166-1 alpha-2 country code. Examples: 'US', 'GB', 'DE', 'FR', 'JP'
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
            "name": "PublicHolidays_check_is_holiday",
            "arguments": {"date": date, "countryCode": countryCode},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PublicHolidays_check_is_holiday"]
