"""
AviationWeather_get_metar

Get real-time METAR weather observations for airports from the Aviation Weather Center (AWC). MET...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def AviationWeather_get_metar(
    ids: str,
    hoursBeforeNow: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get real-time METAR weather observations for airports from the Aviation Weather Center (AWC). MET...

    Parameters
    ----------
    ids : str
        ICAO airport code(s), comma-separated. Examples: 'KLAX' (Los Angeles), 'KJFK'...
    hoursBeforeNow : int | Any
        Hours of data to retrieve (1-24). Default: 1 (most recent METAR only)
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
            "name": "AviationWeather_get_metar",
            "arguments": {"ids": ids, "hoursBeforeNow": hoursBeforeNow},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AviationWeather_get_metar"]
