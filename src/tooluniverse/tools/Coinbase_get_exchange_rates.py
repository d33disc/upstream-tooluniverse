"""
Coinbase_get_exchange_rates

Get exchange rates for a cryptocurrency against all supported fiat currencies and other cryptocur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Coinbase_get_exchange_rates(
    currency: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get exchange rates for a cryptocurrency against all supported fiat currencies and other cryptocur...

    Parameters
    ----------
    currency : str
        Base cryptocurrency or fiat code. Examples: 'BTC', 'ETH', 'USD', 'EUR', 'SOL'...
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
        {"name": "Coinbase_get_exchange_rates", "arguments": {"currency": currency}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Coinbase_get_exchange_rates"]
