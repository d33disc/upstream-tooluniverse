"""
Deezer_search_artists

Search for music artists on Deezer by name. Returns artist details including name, fan count, and...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Deezer_search_artists(
    q: str,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for music artists on Deezer by name. Returns artist details including name, fan count, and...

    Parameters
    ----------
    q : str
        Artist name to search for. Examples: 'daft punk', 'queen', 'eminem', 'taylor ...
    limit : int | Any
        Number of results (1-100). Default: 25
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
        {"name": "Deezer_search_artists", "arguments": {"q": q, "limit": limit}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Deezer_search_artists"]
