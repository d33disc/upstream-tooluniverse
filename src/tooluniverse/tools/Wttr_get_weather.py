"""
Wttr_get_weather

Get current weather conditions and 3-day forecast for any location worldwide using wttr.in. Retur...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Wttr_get_weather(
    location: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get current weather conditions and 3-day forecast for any location worldwide using wttr.in. Retur...

    Parameters
    ----------
    location : str
        Location to get weather for. Supports: city names ('London', 'New York'), air...
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
        {"name": "Wttr_get_weather", "arguments": {"location": location}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Wttr_get_weather"]
