"""
LaunchLibrary_get_upcoming_launches

Get upcoming rocket launches worldwide from The Space Devs Launch Library 2 API. Returns launch d...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def LaunchLibrary_get_upcoming_launches(
    search: Optional[str | Any] = None,
    launch_service_provider__name: Optional[str | Any] = None,
    net__gte: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get upcoming rocket launches worldwide from The Space Devs Launch Library 2 API. Returns launch d...

    Parameters
    ----------
    search : str | Any
        Search text to filter launches by name. Examples: 'Starlink', 'Crew Dragon', ...
    launch_service_provider__name : str | Any
        Filter by launch provider name. Examples: 'SpaceX', 'NASA', 'Rocket Lab', 'Un...
    net__gte : str | Any
        Filter launches after this datetime (ISO 8601). Example: '2024-01-01T00:00:00Z'
    limit : int | Any
        Number of results to return (default 10, max 100)
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
            "name": "LaunchLibrary_get_upcoming_launches",
            "arguments": {
                "search": search,
                "launch_service_provider__name": launch_service_provider__name,
                "net__gte": net__gte,
                "limit": limit,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LaunchLibrary_get_upcoming_launches"]
