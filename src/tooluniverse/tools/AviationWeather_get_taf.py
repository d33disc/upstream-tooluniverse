"""
AviationWeather_get_taf

Get Terminal Aerodrome Forecasts (TAF) for airports from the Aviation Weather Center. TAF provide...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def AviationWeather_get_taf(
    ids: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Terminal Aerodrome Forecasts (TAF) for airports from the Aviation Weather Center. TAF provide...

    Parameters
    ----------
    ids : str
        ICAO airport code(s), comma-separated. Examples: 'KLAX', 'KJFK,KORD', 'EGLL',...
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
        {"name": "AviationWeather_get_taf", "arguments": {"ids": ids}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AviationWeather_get_taf"]
