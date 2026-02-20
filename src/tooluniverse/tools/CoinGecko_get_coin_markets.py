"""
CoinGecko_get_coin_markets

Get ranked cryptocurrency market data from CoinGecko. Returns a list of coins sorted by market ca...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CoinGecko_get_coin_markets(
    vs_currency: str,
    order: Optional[str | Any] = None,
    per_page: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get ranked cryptocurrency market data from CoinGecko. Returns a list of coins sorted by market ca...

    Parameters
    ----------
    vs_currency : str
        Target currency for prices. Examples: 'usd', 'eur', 'btc', 'eth'
    order : str | Any
        Sort order. Options: 'market_cap_desc' (default), 'market_cap_asc', 'volume_d...
    per_page : int | Any
        Number of results per page (1-250). Default: 100
    page : int | Any
        Page number for pagination. Default: 1
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
            "name": "CoinGecko_get_coin_markets",
            "arguments": {
                "vs_currency": vs_currency,
                "order": order,
                "per_page": per_page,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CoinGecko_get_coin_markets"]
