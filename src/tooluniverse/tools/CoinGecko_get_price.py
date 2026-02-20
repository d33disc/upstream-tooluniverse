"""
CoinGecko_get_price

Get current cryptocurrency prices from CoinGecko. Returns real-time prices for one or more crypto...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CoinGecko_get_price(
    ids: str,
    vs_currencies: Optional[str | Any] = None,
    include_24hr_change: Optional[str | Any] = None,
    include_market_cap: Optional[str | Any] = None,
    include_24hr_vol: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get current cryptocurrency prices from CoinGecko. Returns real-time prices for one or more crypto...

    Parameters
    ----------
    ids : str
        Comma-separated cryptocurrency IDs (CoinGecko IDs, NOT ticker symbols). Examp...
    vs_currencies : str | Any
        Comma-separated fiat currency codes for price conversion. Examples: 'usd', 'u...
    include_24hr_change : str | Any
        Include 24-hour price change percentage. Set to 'true' to include. Default: '...
    include_market_cap : str | Any
        Include market capitalization. Set to 'true' to include. Default: 'false'
    include_24hr_vol : str | Any
        Include 24-hour trading volume. Set to 'true' to include. Default: 'false'
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
            "name": "CoinGecko_get_price",
            "arguments": {
                "ids": ids,
                "vs_currencies": vs_currencies,
                "include_24hr_change": include_24hr_change,
                "include_market_cap": include_market_cap,
                "include_24hr_vol": include_24hr_vol,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CoinGecko_get_price"]
