"""
OpenF1_get_meeting_info

Get Formula 1 Grand Prix meeting information using the OpenF1 API. Returns meeting details includ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenF1_get_meeting_info(
    year: Optional[int | Any] = None,
    country_name: Optional[str | Any] = None,
    circuit_short_name: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Formula 1 Grand Prix meeting information using the OpenF1 API. Returns meeting details includ...

    Parameters
    ----------
    year : int | Any
        Season year. Examples: 2023, 2024
    country_name : str | Any
        Filter by country name. Examples: 'Italy', 'Monaco', 'United Kingdom', 'Japan...
    circuit_short_name : str | Any
        Short circuit name. Examples: 'monza', 'spa', 'silverstone', 'monaco'
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
            "name": "OpenF1_get_meeting_info",
            "arguments": {
                "year": year,
                "country_name": country_name,
                "circuit_short_name": circuit_short_name,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenF1_get_meeting_info"]
