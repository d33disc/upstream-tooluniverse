"""
RickAndMorty_get_characters

Get Rick and Morty characters with optional filtering by name, status, species, type, or gender u...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RickAndMorty_get_characters(
    name: Optional[str | Any] = None,
    status: Optional[str | Any] = None,
    species: Optional[str | Any] = None,
    gender: Optional[str | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Rick and Morty characters with optional filtering by name, status, species, type, or gender u...

    Parameters
    ----------
    name : str | Any
        Filter by character name. Examples: 'rick', 'morty', 'beth', 'jerry', 'summer'
    status : str | Any
        Filter by status. Values: 'alive', 'dead', 'unknown'
    species : str | Any
        Filter by species. Examples: 'human', 'alien', 'robot', 'humanoid'
    gender : str | Any
        Filter by gender. Values: 'female', 'male', 'genderless', 'unknown'
    page : int | Any
        Page number for pagination (20 results per page). Default: 1
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
            "name": "RickAndMorty_get_characters",
            "arguments": {
                "name": name,
                "status": status,
                "species": species,
                "gender": gender,
                "page": page,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RickAndMorty_get_characters"]
