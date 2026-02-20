"""
ErgastF1_get_race_results

Get Formula 1 race results for a specific season and round from the Ergast API (via Jolpi mirror)...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ErgastF1_get_race_results(
    season: str,
    round: str,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Formula 1 race results for a specific season and round from the Ergast API (via Jolpi mirror)...

    Parameters
    ----------
    season : str
        F1 season year (e.g., '2024', '2023', '1950'). Use 'current' for the current ...
    round : str
        Race round number within the season (e.g., '1' for first race, '5' for fifth)
    limit : int | Any
        Maximum number of result entries to return (default: 30)
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
            "name": "ErgastF1_get_race_results",
            "arguments": {"season": season, "round": round, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ErgastF1_get_race_results"]
