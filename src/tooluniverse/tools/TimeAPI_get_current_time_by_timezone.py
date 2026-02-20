"""
TimeAPI_get_current_time_by_timezone

Get the current date and time for any timezone using the TimeAPI.io service. Returns year, month,...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TimeAPI_get_current_time_by_timezone(
    timeZone: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current date and time for any timezone using the TimeAPI.io service. Returns year, month,...

    Parameters
    ----------
    timeZone : str
        IANA timezone name. Examples: 'America/New_York', 'Europe/London', 'Asia/Toky...
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
            "name": "TimeAPI_get_current_time_by_timezone",
            "arguments": {"timeZone": timeZone},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TimeAPI_get_current_time_by_timezone"]
