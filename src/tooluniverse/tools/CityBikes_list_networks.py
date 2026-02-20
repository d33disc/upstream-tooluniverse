"""
CityBikes_list_networks

List all bike-sharing networks worldwide available in the CityBikes API. Returns 800+ networks ac...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CityBikes_list_networks(
    fields: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List all bike-sharing networks worldwide available in the CityBikes API. Returns 800+ networks ac...

    Parameters
    ----------
    fields : str | Any
        Comma-separated fields to include. Default: all. Options: id, name, location,...
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
        {"name": "CityBikes_list_networks", "arguments": {"fields": fields}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CityBikes_list_networks"]
