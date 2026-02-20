"""
MusicBrainz_search_artists

Search for music artists in the MusicBrainz open music encyclopedia. Returns artist name, disambi...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MusicBrainz_search_artists(
    query: str,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for music artists in the MusicBrainz open music encyclopedia. Returns artist name, disambi...

    Parameters
    ----------
    query : str
        Artist search query. Examples: 'beatles', 'david bowie', 'radiohead', 'mozart...
    limit : int | Any
        Number of results (1-100). Default: 10
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
            "name": "MusicBrainz_search_artists",
            "arguments": {"query": query, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MusicBrainz_search_artists"]
