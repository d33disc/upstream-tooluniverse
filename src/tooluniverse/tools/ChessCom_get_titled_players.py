"""
ChessCom_get_titled_players

Get a list of Chess.com usernames for players with a specific FIDE title (GM, IM, FM, etc.) using...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ChessCom_get_titled_players(
    title_abbrev: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a list of Chess.com usernames for players with a specific FIDE title (GM, IM, FM, etc.) using...

    Parameters
    ----------
    title_abbrev : str
        FIDE title abbreviation. Values: 'GM' (Grandmaster), 'WGM' (Women's GM), 'IM'...
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
            "name": "ChessCom_get_titled_players",
            "arguments": {"title_abbrev": title_abbrev},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ChessCom_get_titled_players"]
