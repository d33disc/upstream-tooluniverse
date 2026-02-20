"""
Discogs_search_music

Search the Discogs music database for releases (albums, singles, EPs), artists, labels, and maste...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Discogs_search_music(
    q: str,
    type_: Optional[str | Any] = None,
    artist: Optional[str | Any] = None,
    year: Optional[str | Any] = None,
    genre: Optional[str | Any] = None,
    style: Optional[str | Any] = None,
    country: Optional[str | Any] = None,
    per_page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search the Discogs music database for releases (albums, singles, EPs), artists, labels, and maste...

    Parameters
    ----------
    q : str
        Search query. Examples: 'Dark Side of the Moon', 'Led Zeppelin', 'Jazz 1960',...
    type_ : str | Any
        Result type filter. Values: 'release', 'artist', 'label', 'master'. Default: ...
    artist : str | Any
        Filter by artist name. Example: 'Pink Floyd'
    year : str | Any
        Filter by release year. Example: '1973'
    genre : str | Any
        Filter by genre. Examples: 'Rock', 'Jazz', 'Classical', 'Electronic', 'Hip Hop'
    style : str | Any
        Filter by style. Examples: 'Prog Rock', 'Bebop', 'Baroque', 'Techno'
    country : str | Any
        Filter by country of release. Examples: 'US', 'UK', 'Germany'
    per_page : int | Any
        Results per page (default 10, max 100)
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
            "name": "Discogs_search_music",
            "arguments": {
                "q": q,
                "type": type_,
                "artist": artist,
                "year": year,
                "genre": genre,
                "style": style,
                "country": country,
                "per_page": per_page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Discogs_search_music"]
