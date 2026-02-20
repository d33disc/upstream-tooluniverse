"""
OpenLigaDB_get_matches

Get match results for a specific matchday (Spieltag) of a football/soccer league season from Open...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLigaDB_get_matches(
    league: str,
    season: int,
    matchday: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get match results for a specific matchday (Spieltag) of a football/soccer league season from Open...

    Parameters
    ----------
    league : str
        League shortcut code. Examples: 'bl1' (1. Bundesliga), 'bl2' (2. Bundesliga),...
    season : int
        Season year (start year). Examples: 2023 for 2023/2024 season, 2024 for 2024/...
    matchday : int
        Matchday number (Spieltag). Typically 1-34 for Bundesliga regular season.
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
            "name": "OpenLigaDB_get_matches",
            "arguments": {"league": league, "season": season, "matchday": matchday},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLigaDB_get_matches"]
