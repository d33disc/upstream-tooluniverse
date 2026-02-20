"""
Frankfurter_get_exchange_rates

Get current or historical currency exchange rates using the Frankfurter API (European Central Ban...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Frankfurter_get_exchange_rates(
    base: Optional[str | Any] = None,
    to: Optional[str | Any] = None,
    date: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get current or historical currency exchange rates using the Frankfurter API (European Central Ban...

    Parameters
    ----------
    base : str | Any
        Base currency code. Default: EUR. Examples: 'USD', 'EUR', 'GBP', 'JPY', 'CHF'...
    to : str | Any
        Target currencies (comma-separated). Default: all 33 currencies. Examples: 'U...
    date : str | Any
        Historical date in YYYY-MM-DD format. Omit for latest rates. Data available f...
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
            "name": "Frankfurter_get_exchange_rates",
            "arguments": {"base": base, "to": to, "date": date},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Frankfurter_get_exchange_rates"]
