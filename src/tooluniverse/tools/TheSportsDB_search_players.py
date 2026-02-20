"""
TheSportsDB_search_players

Search for sports players by name in TheSportsDB. Returns player details including nationality, p...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheSportsDB_search_players(
    p: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for sports players by name in TheSportsDB. Returns player details including nationality, p...

    Parameters
    ----------
    p : str
        Player name to search for (partial match). Examples: 'Ronaldo', 'LeBron James...
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
        {"name": "TheSportsDB_search_players", "arguments": {"p": p}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheSportsDB_search_players"]
