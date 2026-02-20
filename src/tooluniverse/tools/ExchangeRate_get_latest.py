"""
ExchangeRate_get_latest

Get the latest currency exchange rates relative to a base currency. Uses the Open Exchange Rates ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ExchangeRate_get_latest(
    base: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the latest currency exchange rates relative to a base currency. Uses the Open Exchange Rates ...

    Parameters
    ----------
    base : str | Any
        Base currency code (ISO 4217). All other rates are relative to this. Examples...
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
        {"name": "ExchangeRate_get_latest", "arguments": {"base": base}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ExchangeRate_get_latest"]
