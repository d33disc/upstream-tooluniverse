"""
CountriesNow_get_countries_cities

Get a list of countries with their major cities from the CountriesNow API. Returns all 227 countr...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CountriesNow_get_countries_cities(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a list of countries with their major cities from the CountriesNow API. Returns all 227 countr...

    Parameters
    ----------
    No parameters
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
        {"name": "CountriesNow_get_countries_cities", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CountriesNow_get_countries_cities"]
