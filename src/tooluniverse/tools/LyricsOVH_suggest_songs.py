"""
LyricsOVH_suggest_songs

Search for songs and artists using the Lyrics.ovh suggestion API. Returns a list of songs matchin...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def LyricsOVH_suggest_songs(
    query: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for songs and artists using the Lyrics.ovh suggestion API. Returns a list of songs matchin...

    Parameters
    ----------
    query : str
        Search query for artist or song name. Examples: 'Michael Jackson', 'Beatles',...
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
        {"name": "LyricsOVH_suggest_songs", "arguments": {"query": query}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LyricsOVH_suggest_songs"]
