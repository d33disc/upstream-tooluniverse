"""
Coinbase_get_spot_price

Get the current spot price of a cryptocurrency in any fiat currency using the Coinbase API. Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Coinbase_get_spot_price(
    currency_pair: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current spot price of a cryptocurrency in any fiat currency using the Coinbase API. Retur...

    Parameters
    ----------
    currency_pair : str
        Currency pair in format CRYPTO-FIAT. Examples: 'BTC-USD', 'ETH-EUR', 'SOL-GBP...
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
            "name": "Coinbase_get_spot_price",
            "arguments": {"currency_pair": currency_pair},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Coinbase_get_spot_price"]
