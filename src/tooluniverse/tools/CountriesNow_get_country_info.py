"""
CountriesNow_get_country_info

Get detailed country information including population, area, currency, phone dial code, timezone,...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CountriesNow_get_country_info(
    country: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed country information including population, area, currency, phone dial code, timezone,...

    Parameters
    ----------
    country : str
        Country name. Examples: 'Germany', 'Japan', 'Brazil', 'United States', 'India...
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
        {"name": "CountriesNow_get_country_info", "arguments": {"country": country}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CountriesNow_get_country_info"]
