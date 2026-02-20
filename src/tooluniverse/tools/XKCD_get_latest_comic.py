"""
XKCD_get_latest_comic

Get the latest XKCD comic metadata including title, image URL, alt text, and transcript. XKCD is ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def XKCD_get_latest_comic(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the latest XKCD comic metadata including title, image URL, alt text, and transcript. XKCD is ...

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
        {"name": "XKCD_get_latest_comic", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["XKCD_get_latest_comic"]
