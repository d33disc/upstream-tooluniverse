"""
OpenF1_get_sessions

Get Formula 1 race sessions (Race, Qualifying, Practice) data using the OpenF1 API. Returns sessi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenF1_get_sessions(
    year: Optional[int | Any] = None,
    session_name: Optional[str | Any] = None,
    circuit_short_name: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Formula 1 race sessions (Race, Qualifying, Practice) data using the OpenF1 API. Returns sessi...

    Parameters
    ----------
    year : int | Any
        Season year. Examples: 2023, 2024
    session_name : str | Any
        Filter by session type. Values: 'Race', 'Qualifying', 'Sprint', 'Practice 1',...
    circuit_short_name : str | Any
        Short circuit name. Examples: 'monza', 'spa', 'silverstone', 'monaco', 'suzuk...
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
            "name": "OpenF1_get_sessions",
            "arguments": {
                "year": year,
                "session_name": session_name,
                "circuit_short_name": circuit_short_name,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenF1_get_sessions"]
