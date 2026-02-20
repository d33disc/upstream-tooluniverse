"""
RESTCountries_get_by_subregion

Get all countries in a geographic subregion using the REST Countries API. Returns country data fo...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RESTCountries_get_by_subregion(
    subregion: str,
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get all countries in a geographic subregion using the REST Countries API. Returns country data fo...

    Parameters
    ----------
    subregion : str
        Geographic subregion. Examples: 'Northern Europe', 'Southeast Asia', 'Western...
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
            "name": "RESTCountries_get_by_subregion",
            "arguments": {"subregion": subregion, "fields": fields},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RESTCountries_get_by_subregion"]
