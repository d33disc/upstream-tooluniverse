"""
Deezer_get_artist_top_tracks

Get the top tracks for a specific Deezer artist by their artist ID. Returns the most popular song...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Deezer_get_artist_top_tracks(
    artist_id: int,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the top tracks for a specific Deezer artist by their artist ID. Returns the most popular song...

    Parameters
    ----------
    artist_id : int
        Deezer artist ID. Examples: 27 (Daft Punk), 13 (Eminem), 12246 (Taylor Swift)...
    limit : int | Any
        Number of top tracks to return (1-50). Default: 10
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
            "name": "Deezer_get_artist_top_tracks",
            "arguments": {"artist_id": artist_id, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Deezer_get_artist_top_tracks"]
