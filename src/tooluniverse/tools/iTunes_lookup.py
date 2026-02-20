"""
iTunes_lookup

Look up a specific item in the iTunes Store by its Apple ID (artist, album, track, app, etc.). Re...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iTunes_lookup(
    id: str,
    entity: Optional[str | Any] = None,
    limit: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Look up a specific item in the iTunes Store by its Apple ID (artist, album, track, app, etc.). Re...

    Parameters
    ----------
    id : str
        Apple iTunes ID to look up. Examples: '657515' (Radiohead artist), '144083309...
    entity : str | Any
        Related entity type to return. For artist lookup: 'album', 'song'. For album:...
    limit : int | Any
        Number of related items to return (1-200). Default: 50
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
            "name": "iTunes_lookup",
            "arguments": {"id": id, "entity": entity, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iTunes_lookup"]
