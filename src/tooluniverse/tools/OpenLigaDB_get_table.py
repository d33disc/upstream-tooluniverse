"""
OpenLigaDB_get_table

Get the league standings table for a specific football/soccer season from OpenLigaDB. Returns the...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLigaDB_get_table(
    league: str,
    season: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the league standings table for a specific football/soccer season from OpenLigaDB. Returns the...

    Parameters
    ----------
    league : str
        League shortcut code. Examples: 'bl1' (1. Bundesliga), 'bl2' (2. Bundesliga),...
    season : int
        Season year (start year). Examples: 2023 for 2023/2024 season
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
            "name": "OpenLigaDB_get_table",
            "arguments": {"league": league, "season": season},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLigaDB_get_table"]
