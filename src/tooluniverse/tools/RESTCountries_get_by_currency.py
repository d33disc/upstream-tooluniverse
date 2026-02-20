"""
RESTCountries_get_by_currency

Find all countries that use a specific currency using the REST Countries API. Returns full countr...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RESTCountries_get_by_currency(
    currency: str,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Find all countries that use a specific currency using the REST Countries API. Returns full countr...

    Parameters
    ----------
    currency : str
        Currency code (e.g., 'EUR', 'USD', 'GBP') or currency name (e.g., 'euro', 'do...
    fields : str | Any
        Comma-separated fields to return. Examples: 'name,capital,currencies', 'name,...
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
            "name": "RESTCountries_get_by_currency",
            "arguments": {"currency": currency, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RESTCountries_get_by_currency"]
