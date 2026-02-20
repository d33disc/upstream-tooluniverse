"""
PublicHolidays_get_by_country

Get public holidays for a specific country and year using the Nager.Date API. Returns holiday dat...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def PublicHolidays_get_by_country(
    year: int,
    countryCode: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get public holidays for a specific country and year using the Nager.Date API. Returns holiday dat...

    Parameters
    ----------
    year : int
        Year to get holidays for. Examples: 2024, 2025, 2026
    countryCode : str
        ISO 3166-1 alpha-2 country code. Examples: 'US' (USA), 'GB' (UK), 'DE' (Germa...
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
            "name": "PublicHolidays_get_by_country",
            "arguments": {"year": year, "countryCode": countryCode},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["PublicHolidays_get_by_country"]
