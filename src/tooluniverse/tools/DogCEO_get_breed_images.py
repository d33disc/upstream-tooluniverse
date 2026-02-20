"""
DogCEO_get_breed_images

Get random images of a specific dog breed from the Dog CEO API. Returns URLs to high-quality dog ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DogCEO_get_breed_images(
    breed: str,
    count: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get random images of a specific dog breed from the Dog CEO API. Returns URLs to high-quality dog ...

    Parameters
    ----------
    breed : str
        Dog breed name (lowercase). For sub-breeds, use 'breed/sub-breed' format. Exa...
    count : int | Any
        Number of random images to return (1-50). Default: 1. Example: 3
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
            "name": "DogCEO_get_breed_images",
            "arguments": {"breed": breed, "count": count},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DogCEO_get_breed_images"]
