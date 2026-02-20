"""
TVmaze_search_shows

Search for TV shows in the TVmaze database, which covers 45,000+ shows with ratings, genres, netw...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TVmaze_search_shows(
    q: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for TV shows in the TVmaze database, which covers 45,000+ shows with ratings, genres, netw...

    Parameters
    ----------
    q : str
        Search query (show title). Examples: 'Breaking Bad', 'Game of Thrones', 'The ...
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
        {"name": "TVmaze_search_shows", "arguments": {"q": q}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TVmaze_search_shows"]
