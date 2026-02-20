"""
MemeAPI_get_random_meme

Get a random internet meme from Reddit using the Meme API (meme-api.com). Returns meme title, ima...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MemeAPI_get_random_meme(
    subreddit: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random internet meme from Reddit using the Meme API (meme-api.com). Returns meme title, ima...

    Parameters
    ----------
    subreddit : str | Any
        Optional Reddit subreddit to get meme from. Examples: 'memes', 'dankmemes', '...
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
        {"name": "MemeAPI_get_random_meme", "arguments": {"subreddit": subreddit}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MemeAPI_get_random_meme"]
