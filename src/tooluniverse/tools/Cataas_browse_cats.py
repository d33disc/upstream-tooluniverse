"""
Cataas_browse_cats

Browse cat images from the Cat as a Service (CATAAS) API. Returns a paginated list of cat image m...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Cataas_browse_cats(
    tags: Optional[str | Any] = None,
    skip: Optional[int | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Browse cat images from the Cat as a Service (CATAAS) API. Returns a paginated list of cat image m...

    Parameters
    ----------
    tags : str | Any
        Filter by tag (e.g., 'cute', 'funny', 'sleeping', 'black', 'orange'). Leave n...
    skip : int | Any
        Number of results to skip for pagination (default 0)
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
            "name": "Cataas_browse_cats",
            "arguments": {"tags": tags, "skip": skip, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Cataas_browse_cats"]
