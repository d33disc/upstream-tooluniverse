"""
OnThisDay_get_events

Get historical events, births, and deaths that occurred on a specific day in history using the by...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OnThisDay_get_events(
    month: int,
    day: int,
    type_: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get historical events, births, and deaths that occurred on a specific day in history using the by...

    Parameters
    ----------
    month : int
        Month number (1-12). Examples: 1 (January), 7 (July), 12 (December)
    day : int
        Day of month (1-31). Examples: 1, 15, 25
    type_ : str | Any
        Type of historical data. Values: 'events' (historical events), 'births' (nota...
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
            "name": "OnThisDay_get_events",
            "arguments": {"month": month, "day": day, "type": type_},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OnThisDay_get_events"]
