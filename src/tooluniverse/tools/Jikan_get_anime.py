"""
Jikan_get_anime

Get detailed information about a specific anime by its MyAnimeList ID. Returns comprehensive data...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Jikan_get_anime(
    mal_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific anime by its MyAnimeList ID. Returns comprehensive data...

    Parameters
    ----------
    mal_id : int
        MyAnimeList anime ID (e.g., 1 for Cowboy Bebop, 20 for Naruto, 16498 for Atta...
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
        {"name": "Jikan_get_anime", "arguments": {"mal_id": mal_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Jikan_get_anime"]
