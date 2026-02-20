"""
SpaceX_get_launch

Get detailed data about a specific SpaceX launch by its ID. Returns mission name, date, success s...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SpaceX_get_launch(
    launch_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed data about a specific SpaceX launch by its ID. Returns mission name, date, success s...

    Parameters
    ----------
    launch_id : str
        The SpaceX launch ID (24-character hex string)
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
        {"name": "SpaceX_get_launch", "arguments": {"launch_id": launch_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SpaceX_get_launch"]
