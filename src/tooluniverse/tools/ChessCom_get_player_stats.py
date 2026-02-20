"""
ChessCom_get_player_stats

Get a Chess.com player's game statistics including ratings for bullet, blitz, rapid, and daily ch...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ChessCom_get_player_stats(
    username: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a Chess.com player's game statistics including ratings for bullet, blitz, rapid, and daily ch...

    Parameters
    ----------
    username : str
        Chess.com username. Examples: 'magnuscarlsen', 'hikaru', 'fabianocaruana', 'a...
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
        {"name": "ChessCom_get_player_stats", "arguments": {"username": username}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ChessCom_get_player_stats"]
