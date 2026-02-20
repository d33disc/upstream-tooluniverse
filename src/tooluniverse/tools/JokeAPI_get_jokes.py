"""
JokeAPI_get_jokes

Get random jokes from JokeAPI v2, a free REST API serving jokes in multiple categories. Returns j...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def JokeAPI_get_jokes(
    category: Optional[str | Any] = None,
    amount: Optional[int | Any] = None,
    type_: Optional[str | Any] = None,
    blacklistFlags: Optional[str | Any] = None,
    safe_mode: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get random jokes from JokeAPI v2, a free REST API serving jokes in multiple categories. Returns j...

    Parameters
    ----------
    category : str | Any
        Joke category filter. Options: 'Any' (default, all categories), 'Programming'...
    amount : int | Any
        Number of jokes to return (1-10). Default is 1. When amount > 1, response con...
    type_ : str | Any
        Joke format filter. Options: 'single' (one-liner jokes only), 'twopart' (setu...
    blacklistFlags : str | Any
        Comma-separated content flags to exclude. Options: 'nsfw', 'religious', 'poli...
    safe_mode : str | Any
        Set to any value (e.g., '') to enable safe mode, which is equivalent to black...
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
            "name": "JokeAPI_get_jokes",
            "arguments": {
                "category": category,
                "amount": amount,
                "type": type_,
                "blacklistFlags": blacklistFlags,
                "safe-mode": safe_mode,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["JokeAPI_get_jokes"]
