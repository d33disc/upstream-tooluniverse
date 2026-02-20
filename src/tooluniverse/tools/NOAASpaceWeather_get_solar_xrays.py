"""
NOAASpaceWeather_get_solar_xrays

Get recent solar X-ray flux measurements from NOAA GOES satellite (last 7 days). X-ray flux is us...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NOAASpaceWeather_get_solar_xrays(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get recent solar X-ray flux measurements from NOAA GOES satellite (last 7 days). X-ray flux is us...

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
        {"name": "NOAASpaceWeather_get_solar_xrays", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NOAASpaceWeather_get_solar_xrays"]
