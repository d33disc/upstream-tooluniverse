"""
FreeToGame_get_games

Get a list of free-to-play PC and browser games from the FreeToGame API. Returns game titles, des...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def FreeToGame_get_games(
    platform: Optional[str | Any] = None,
    category: Optional[str | Any] = None,
    sort_by: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a list of free-to-play PC and browser games from the FreeToGame API. Returns game titles, des...

    Parameters
    ----------
    platform : str | Any
        Platform filter. Values: 'pc' (Windows games), 'browser' (browser games), 'al...
    category : str | Any
        Genre/category filter. Values: 'mmorpg', 'shooter', 'strategy', 'moba', 'raci...
    sort_by : str | Any
        Sort order. Values: 'release-date', 'popularity' (default), 'alphabetical', '...
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
            "name": "FreeToGame_get_games",
            "arguments": {
                "platform": platform,
                "category": category,
                "sort-by": sort_by,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FreeToGame_get_games"]
