"""
NOAASpaceWeather_get_solar_cycle

Get predicted solar cycle data from NOAA Space Weather Prediction Center (SWPC). Returns monthly ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NOAASpaceWeather_get_solar_cycle(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get predicted solar cycle data from NOAA Space Weather Prediction Center (SWPC). Returns monthly ...

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
        {"name": "NOAASpaceWeather_get_solar_cycle", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NOAASpaceWeather_get_solar_cycle"]
