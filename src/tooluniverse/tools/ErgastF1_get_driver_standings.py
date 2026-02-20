"""
ErgastF1_get_driver_standings

Get Formula 1 World Drivers' Championship standings for a specific season from the Ergast API (vi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ErgastF1_get_driver_standings(
    season: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Formula 1 World Drivers' Championship standings for a specific season from the Ergast API (vi...

    Parameters
    ----------
    season : str
        F1 season year (e.g., '2024', '2023'). Use 'current' for the current season.
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
        {"name": "ErgastF1_get_driver_standings", "arguments": {"season": season}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ErgastF1_get_driver_standings"]
