"""
NagerDate_get_public_holidays

Get official public holidays for any country and year using the Nager.Date API. Covers 120 countr...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NagerDate_get_public_holidays(
    year: int,
    countryCode: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get official public holidays for any country and year using the Nager.Date API. Covers 120 countr...

    Parameters
    ----------
    year : int
        Year to get holidays for. Examples: 2024, 2025, 2026
    countryCode : str
        ISO 3166-1 alpha-2 country code. Examples: 'US', 'GB', 'DE', 'FR', 'JP', 'CA'...
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
            "name": "NagerDate_get_public_holidays",
            "arguments": {"year": year, "countryCode": countryCode},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NagerDate_get_public_holidays"]
