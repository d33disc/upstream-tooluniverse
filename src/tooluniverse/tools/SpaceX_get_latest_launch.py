"""
SpaceX_get_latest_launch

Get data about the latest SpaceX rocket launch, including mission name, date, success status, roc...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SpaceX_get_latest_launch(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get data about the latest SpaceX rocket launch, including mission name, date, success status, roc...

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
        {"name": "SpaceX_get_latest_launch", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SpaceX_get_latest_launch"]
