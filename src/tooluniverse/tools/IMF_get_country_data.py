"""
IMF_get_country_data

Get IMF World Economic Outlook (WEO) data for specific countries and economic indicators. Returns...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def IMF_get_country_data(
    indicator: str,
    countries: str,
    periods: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get IMF World Economic Outlook (WEO) data for specific countries and economic indicators. Returns...

    Parameters
    ----------
    indicator : str
        IMF indicator code (e.g., 'NGDP_RPCH' for real GDP growth, 'PCPIPCH' for infl...
    countries : str
        Comma-separated ISO 3166-1 alpha-3 country codes (e.g., 'USA,GBR,DEU' or 'CHN...
    periods : str | Any
        Comma-separated years to retrieve (e.g., '2020,2021,2022,2023' or '2023'). If...
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
            "name": "IMF_get_country_data",
            "arguments": {
                "indicator": indicator,
                "countries": countries,
                "periods": periods,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["IMF_get_country_data"]
