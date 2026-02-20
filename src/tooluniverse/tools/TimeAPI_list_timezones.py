"""
TimeAPI_list_timezones

Get a complete list of all available IANA timezone identifiers from TimeAPI.io. Returns 500+ time...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def TimeAPI_list_timezones(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a complete list of all available IANA timezone identifiers from TimeAPI.io. Returns 500+ time...

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
        {"name": "TimeAPI_list_timezones", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TimeAPI_list_timezones"]
