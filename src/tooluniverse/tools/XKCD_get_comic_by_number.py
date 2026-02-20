"""
XKCD_get_comic_by_number

Get a specific XKCD comic by its number. Returns metadata including title, image URL, alt text, a...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def XKCD_get_comic_by_number(
    comic_number: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a specific XKCD comic by its number. Returns metadata including title, image URL, alt text, a...

    Parameters
    ----------
    comic_number : int
        The XKCD comic number to retrieve
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
            "name": "XKCD_get_comic_by_number",
            "arguments": {"comic_number": comic_number},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["XKCD_get_comic_by_number"]
