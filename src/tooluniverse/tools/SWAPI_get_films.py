"""
SWAPI_get_films

Get Star Wars film data using the Star Wars API (SWAPI). Returns film title, episode ID, opening ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SWAPI_get_films(
    search: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get Star Wars film data using the Star Wars API (SWAPI). Returns film title, episode ID, opening ...

    Parameters
    ----------
    search : str | Any
        Search by film title. Examples: 'hope', 'empire', 'jedi', 'phantom', 'clones'...
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
        {"name": "SWAPI_get_films", "arguments": {"search": search}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SWAPI_get_films"]
