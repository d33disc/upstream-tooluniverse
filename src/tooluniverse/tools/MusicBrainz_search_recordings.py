"""
MusicBrainz_search_recordings

Search for music recordings (songs) in the MusicBrainz open music encyclopedia. Returns title, ar...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MusicBrainz_search_recordings(
    query: str,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for music recordings (songs) in the MusicBrainz open music encyclopedia. Returns title, ar...

    Parameters
    ----------
    query : str
        Lucene search query. Use field:value syntax. Fields: artist (artist name), ti...
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
            "name": "MusicBrainz_search_recordings",
            "arguments": {"query": query, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MusicBrainz_search_recordings"]
