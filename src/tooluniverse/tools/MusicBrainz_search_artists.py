"""
MusicBrainz_search_artists

Search MusicBrainz for musical artists, bands, and composers. MusicBrainz is the world's largest ...
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
    Search MusicBrainz for musical artists, bands, and composers. MusicBrainz is the world's largest ...

    Parameters
    ----------
    query : str
        Artist name or search query. Supports Lucene syntax: 'artist:Beatles', 'count...
    limit : int | Any
        Maximum results to return (1-100, default 25)
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
