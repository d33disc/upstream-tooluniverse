"""
OfficialJoke_get_random_joke

Get random jokes from the Official Joke API. Returns setup and punchline for general, programming...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OfficialJoke_get_random_joke(
    type_: Optional[str | Any] = None,
    count: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get random jokes from the Official Joke API. Returns setup and punchline for general, programming...

    Parameters
    ----------
    type_ : str | Any
        Joke category. Values: 'general', 'programming', 'knock-knock', 'dad'. Omit f...
    count : int | Any
        Number of jokes to return (1-10). Default: 1
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
            "name": "OfficialJoke_get_random_joke",
            "arguments": {"type": type_, "count": count},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OfficialJoke_get_random_joke"]
