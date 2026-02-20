"""
BoredAPI_get_activity_by_key

Get a specific activity by its unique key from the Bored API. Useful for retrieving a previously ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def BoredAPI_get_activity_by_key(
    key: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a specific activity by its unique key from the Bored API. Useful for retrieving a previously ...

    Parameters
    ----------
    key : str
        The unique activity key. Example: '2715253'
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
        {"name": "BoredAPI_get_activity_by_key", "arguments": {"key": key}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["BoredAPI_get_activity_by_key"]
