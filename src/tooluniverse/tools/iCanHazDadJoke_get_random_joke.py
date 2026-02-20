"""
iCanHazDadJoke_get_random_joke

Get a random dad joke from the icanhazdadjoke.com API. Returns a setup-punchline style joke with ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def iCanHazDadJoke_get_random_joke(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random dad joke from the icanhazdadjoke.com API. Returns a setup-punchline style joke with ...

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
        {"name": "iCanHazDadJoke_get_random_joke", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["iCanHazDadJoke_get_random_joke"]
