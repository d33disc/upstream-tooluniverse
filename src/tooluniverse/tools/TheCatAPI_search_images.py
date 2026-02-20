"""
TheCatAPI_search_images

Search for cat images from TheCatAPI. Returns random cat image URLs optionally filtered by breed....
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TheCatAPI_search_images(
    limit: Optional[int | Any] = None,
    breed_ids: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for cat images from TheCatAPI. Returns random cat image URLs optionally filtered by breed....

    Parameters
    ----------
    limit : int | Any
        Number of images to return (1-10, default: 1)
    breed_ids : str | Any
        Filter by breed ID(s), comma-separated. Examples: 'pers' (Persian), 'siam' (S...
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
            "name": "TheCatAPI_search_images",
            "arguments": {"limit": limit, "breed_ids": breed_ids},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TheCatAPI_search_images"]
