"""
ExchangeRate_get_latest_rates

Get current foreign exchange rates for 166 currencies using the ExchangeRate-API free endpoint. R...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ExchangeRate_get_latest_rates(
    base: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get current foreign exchange rates for 166 currencies using the ExchangeRate-API free endpoint. R...

    Parameters
    ----------
    base : str
        Base currency ISO 4217 code to get rates relative to. Examples: 'USD' (US Dol...
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
        {"name": "ExchangeRate_get_latest_rates", "arguments": {"base": base}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ExchangeRate_get_latest_rates"]
