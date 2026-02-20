"""
CoinGecko_get_coin_price

Get current price, market cap, and 24h change for one or more cryptocurrencies using the CoinGeck...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CoinGecko_get_coin_price(
    ids: str,
    vs_currencies: Optional[str | Any] = None,
    include_market_cap: Optional[str | Any] = None,
    include_24hr_change: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get current price, market cap, and 24h change for one or more cryptocurrencies using the CoinGeck...

    Parameters
    ----------
    ids : str
        Comma-separated coin IDs. Examples: 'bitcoin', 'bitcoin,ethereum', 'bitcoin,e...
    vs_currencies : str | Any
        Target currency for prices, comma-separated. Default: 'usd'. Examples: 'usd',...
    include_market_cap : str | Any
        Include market cap in response. Values: 'true', 'false'. Default: false
    include_24hr_change : str | Any
        Include 24h price change percentage. Values: 'true', 'false'. Default: false
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
            "name": "CoinGecko_get_coin_price",
            "arguments": {
                "ids": ids,
                "vs_currencies": vs_currencies,
                "include_market_cap": include_market_cap,
                "include_24hr_change": include_24hr_change,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CoinGecko_get_coin_price"]
