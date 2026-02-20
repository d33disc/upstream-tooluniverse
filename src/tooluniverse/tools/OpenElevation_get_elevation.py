"""
OpenElevation_get_elevation

Get ground elevation (altitude) data for geographic coordinates using the Open Elevation API. Ret...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenElevation_get_elevation(
    locations: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get ground elevation (altitude) data for geographic coordinates using the Open Elevation API. Ret...

    Parameters
    ----------
    locations : str
        Pipe-separated list of latitude,longitude pairs. Examples: '10,10' (single po...
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
        {"name": "OpenElevation_get_elevation", "arguments": {"locations": locations}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenElevation_get_elevation"]
