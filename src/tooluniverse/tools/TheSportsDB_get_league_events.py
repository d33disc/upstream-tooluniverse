"""
TheSportsDB_get_league_events

Get sports events/matches for a specific season from TheSportsDB. Returns match details including...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheSportsDB_get_league_events(
    id: str,
    s: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get sports events/matches for a specific season from TheSportsDB. Returns match details including...

    Parameters
    ----------
    id : str
        League ID from TheSportsDB. Common IDs: '4328' (English Premier League), '433...
    s : str
        Season (format varies by sport). Soccer: '2023-2024'. Basketball/American spo...
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
        {"name": "TheSportsDB_get_league_events", "arguments": {"id": id, "s": s}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheSportsDB_get_league_events"]
