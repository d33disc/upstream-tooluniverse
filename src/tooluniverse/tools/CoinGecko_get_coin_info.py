"""
CoinGecko_get_coin_info

Get comprehensive information about a specific cryptocurrency from CoinGecko, including descripti...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CoinGecko_get_coin_info(
    id: str,
    localization: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get comprehensive information about a specific cryptocurrency from CoinGecko, including descripti...

    Parameters
    ----------
    id : str
        CoinGecko coin ID. Examples: 'bitcoin', 'ethereum', 'solana', 'cardano', 'pol...
    localization : str | Any
        Include localized names. Values: 'true', 'false'. Default: false (set to fals...
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
            "name": "CoinGecko_get_coin_info",
            "arguments": {"id": id, "localization": localization},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CoinGecko_get_coin_info"]
