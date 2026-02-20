"""
NagerDate_check_is_workday

Check if a specific date is a public holiday or workday for a given country using the Nager.Date ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NagerDate_check_is_workday(
    countryCode: str,
    date: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Check if a specific date is a public holiday or workday for a given country using the Nager.Date ...

    Parameters
    ----------
    countryCode : str
        ISO 3166-1 alpha-2 country code. Examples: 'US', 'GB', 'DE', 'FR', 'JP'
    date : str
        Date to check (YYYY-MM-DD format). Examples: '2025-12-25', '2025-07-04', '202...
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
            "name": "NagerDate_check_is_workday",
            "arguments": {"countryCode": countryCode, "date": date},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NagerDate_check_is_workday"]
