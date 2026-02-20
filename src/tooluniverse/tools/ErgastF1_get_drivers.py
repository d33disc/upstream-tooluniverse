"""
ErgastF1_get_drivers

Get the list of Formula 1 drivers for a specific season from the Ergast API (via Jolpi mirror). R...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ErgastF1_get_drivers(
    season: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the list of Formula 1 drivers for a specific season from the Ergast API (via Jolpi mirror). R...

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
        {"name": "ErgastF1_get_drivers", "arguments": {"season": season}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ErgastF1_get_drivers"]
