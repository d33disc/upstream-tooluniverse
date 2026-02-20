"""
LyricsOVH_get_lyrics

Get lyrics for any song using the Lyrics.ovh API. Returns the full song lyrics as text. Covers a ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def LyricsOVH_get_lyrics(
    artist: str,
    title: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get lyrics for any song using the Lyrics.ovh API. Returns the full song lyrics as text. Covers a ...

    Parameters
    ----------
    artist : str
        Artist or band name. Examples: 'Michael Jackson', 'The Beatles', 'Taylor Swif...
    title : str
        Song title. Examples: 'Thriller', 'Bohemian Rhapsody', 'Hey Jude', 'Shake It ...
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
            "name": "LyricsOVH_get_lyrics",
            "arguments": {"artist": artist, "title": title},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LyricsOVH_get_lyrics"]
