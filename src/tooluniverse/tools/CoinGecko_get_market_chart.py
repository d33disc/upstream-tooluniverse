"""
CoinGecko_get_market_chart

Get historical market data (price, market cap, volume) for a cryptocurrency over time from CoinGe...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CoinGecko_get_market_chart(
    coin_id: str,
    vs_currency: Optional[str | Any] = None,
    days: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get historical market data (price, market cap, volume) for a cryptocurrency over time from CoinGe...

    Parameters
    ----------
    coin_id : str
        CoinGecko cryptocurrency ID. Examples: 'bitcoin', 'ethereum', 'solana'
    vs_currency : str | Any
        Target fiat currency for price data. Examples: 'usd', 'eur', 'gbp'. Default: ...
    days : str | Any
        Number of days of historical data. Examples: '1' (24h), '7' (1 week), '30' (1...
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
            "name": "CoinGecko_get_market_chart",
            "arguments": {"coin_id": coin_id, "vs_currency": vs_currency, "days": days},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CoinGecko_get_market_chart"]
