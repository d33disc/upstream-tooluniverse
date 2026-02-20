"""
DogCEO_get_random_dog_image

Get a random dog image URL using the Dog CEO API. Can filter by breed or sub-breed. Returns URL t...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DogCEO_get_random_dog_image(
    breed: Optional[str | Any] = None,
    sub_breed: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random dog image URL using the Dog CEO API. Can filter by breed or sub-breed. Returns URL t...

    Parameters
    ----------
    breed : str | Any
        Dog breed name (lowercase). Examples: 'labrador', 'poodle', 'husky', 'beagle'...
    sub_breed : str | Any
        Sub-breed if applicable. Examples: for breed='retriever': 'golden', 'labrador...
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
            "name": "DogCEO_get_random_dog_image",
            "arguments": {"breed": breed, "sub_breed": sub_breed},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DogCEO_get_random_dog_image"]
