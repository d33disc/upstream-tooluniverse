"""
iTunes_search_media

Search Apple's iTunes Store catalog for music, movies, podcasts, audiobooks, apps, and more. Retu...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iTunes_search_media(
    term: str,
    media: Optional[str | Any] = None,
    entity: Optional[str | Any] = None,
    country: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Apple's iTunes Store catalog for music, movies, podcasts, audiobooks, apps, and more. Retu...

    Parameters
    ----------
    term : str
        Search query (e.g., 'radiohead', 'inception', 'serial podcast', 'machine lear...
    media : str | Any
        Media type filter. Options: 'music', 'movie', 'podcast', 'audiobook', 'shortF...
    entity : str | Any
        Entity type within media. Music: 'musicTrack', 'album', 'musicArtist'. Movie:...
    country : str | Any
        Two-letter ISO country code for store region (e.g., 'US', 'GB', 'JP'). Defaul...
    limit : int | Any
        Number of results to return (1-200). Default: 10
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
            "name": "iTunes_search_media",
            "arguments": {
                "term": term,
                "media": media,
                "entity": entity,
                "country": country,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iTunes_search_media"]
