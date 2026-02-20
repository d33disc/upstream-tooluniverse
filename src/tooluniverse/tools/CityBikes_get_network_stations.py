"""
CityBikes_get_network_stations

Get real-time station data for a specific bike-sharing network using the CityBikes API. Returns a...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def CityBikes_get_network_stations(
    network_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get real-time station data for a specific bike-sharing network using the CityBikes API. Returns a...

    Parameters
    ----------
    network_id : str
        Network ID from CityBikes_list_networks. Examples: 'santander-cycles', 'citi-...
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
            "name": "CityBikes_get_network_stations",
            "arguments": {"network_id": network_id},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CityBikes_get_network_stations"]
