"""
MusicBrainz_get_artist

Get detailed information about a specific artist from MusicBrainz by their MBID. Returns artist b...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MusicBrainz_get_artist(
    mbid: str,
    inc: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific artist from MusicBrainz by their MBID. Returns artist b...

    Parameters
    ----------
    mbid : str
        MusicBrainz artist ID (MBID, UUID format, e.g., 'b10bbbfc-cf9e-42e0-be17-e2c3...
    inc : str | Any
        Additional data to include: 'release-groups' for albums, 'tags' for genre tag...
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
        {"name": "MusicBrainz_get_artist", "arguments": {"mbid": mbid, "inc": inc}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MusicBrainz_get_artist"]
