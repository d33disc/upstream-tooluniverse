"""
RickAndMorty_get_episodes

Get Rick and Morty episodes with optional filtering by name or episode code (e.g. S01E01) using t...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RickAndMorty_get_episodes(
    name: Optional[str | Any] = None,
    episode: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Rick and Morty episodes with optional filtering by name or episode code (e.g. S01E01) using t...

    Parameters
    ----------
    name : str | Any
        Filter by episode name. Examples: 'pilot', 'rick potion', 'pickle'
    episode : str | Any
        Filter by episode code. Examples: 'S01E01', 'S02E05', 'S03E03'
    page : int | Any
        Page number (20 results per page). Default: 1
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
            "name": "RickAndMorty_get_episodes",
            "arguments": {"name": name, "episode": episode, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RickAndMorty_get_episodes"]
