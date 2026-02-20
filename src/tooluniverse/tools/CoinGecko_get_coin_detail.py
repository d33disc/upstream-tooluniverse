"""
CoinGecko_get_coin_detail

Get comprehensive details about a specific cryptocurrency from CoinGecko. Returns current market ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CoinGecko_get_coin_detail(
    coin_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive details about a specific cryptocurrency from CoinGecko. Returns current market ...

    Parameters
    ----------
    coin_id : str
        CoinGecko cryptocurrency ID. Examples: 'bitcoin', 'ethereum', 'cardano', 'sol...
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
        {"name": "CoinGecko_get_coin_detail", "arguments": {"coin_id": coin_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CoinGecko_get_coin_detail"]
