"""
BoredAPI_get_random_activity

Get a random activity suggestion from the Bored API. Returns an activity with metadata including ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BoredAPI_get_random_activity(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a random activity suggestion from the Bored API. Returns an activity with metadata including ...

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
        {"name": "BoredAPI_get_random_activity", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BoredAPI_get_random_activity"]
