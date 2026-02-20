"""
RESTCountries_get_by_name

Get detailed information about a country by name using the REST Countries API. Returns capital, p...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RESTCountries_get_by_name(
    name: str,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a country by name using the REST Countries API. Returns capital, p...

    Parameters
    ----------
    name : str
        Country name to search. Examples: 'France', 'Brazil', 'Japan', 'South Africa'...
    fields : str | Any
        Comma-separated list of fields to return. Examples: 'name,capital,population'...
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
            "name": "RESTCountries_get_by_name",
            "arguments": {"name": name, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RESTCountries_get_by_name"]
