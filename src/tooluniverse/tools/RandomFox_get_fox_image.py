"""
RandomFox_get_fox_image

Get a random fox image URL using the RandomFox API (randomfox.ca). Returns a unique fox image URL...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def RandomFox_get_fox_image(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random fox image URL using the RandomFox API (randomfox.ca). Returns a unique fox image URL...

    Parameters
    ----------
    No parameters
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
        {"name": "RandomFox_get_fox_image", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["RandomFox_get_fox_image"]
