"""
MemeAPI_get_multiple_memes

Get multiple random memes at once from Reddit using the Meme API (meme-api.com). Returns up to 50...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MemeAPI_get_multiple_memes(
    count: int,
    subreddit: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get multiple random memes at once from Reddit using the Meme API (meme-api.com). Returns up to 50...

    Parameters
    ----------
    count : int
        Number of memes to return (1-50). Default: 5
    subreddit : str | Any
        Optional Reddit subreddit to get memes from. Examples: 'memes', 'programmerhu...
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
            "name": "MemeAPI_get_multiple_memes",
            "arguments": {"count": count, "subreddit": subreddit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MemeAPI_get_multiple_memes"]
