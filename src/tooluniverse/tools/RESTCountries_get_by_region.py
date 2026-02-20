"""
RESTCountries_get_by_region

Get all countries in a geographic region using the REST Countries API. Returns country data for a...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RESTCountries_get_by_region(
    region: str,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get all countries in a geographic region using the REST Countries API. Returns country data for a...

    Parameters
    ----------
    region : str
        Geographic region. Values: 'Africa', 'Americas', 'Asia', 'Europe', 'Oceania',...
    fields : str | Any
        Comma-separated fields to return. Examples: 'name,capital,population', 'name,...
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
            "name": "RESTCountries_get_by_region",
            "arguments": {"region": region, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RESTCountries_get_by_region"]
