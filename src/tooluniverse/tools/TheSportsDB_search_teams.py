"""
TheSportsDB_search_teams

Search for sports teams by name in TheSportsDB - a free community sports database. Returns team d...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheSportsDB_search_teams(
    t: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for sports teams by name in TheSportsDB - a free community sports database. Returns team d...

    Parameters
    ----------
    t : str
        Team name to search for (partial match). Examples: 'Arsenal', 'Manchester Uni...
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
        {"name": "TheSportsDB_search_teams", "arguments": {"t": t}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheSportsDB_search_teams"]
