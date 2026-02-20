"""
SpaceX_list_rockets

List all SpaceX rockets with specifications. Returns data about Falcon 1, Falcon 9, Falcon Heavy,...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SpaceX_list_rockets(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    List all SpaceX rockets with specifications. Returns data about Falcon 1, Falcon 9, Falcon Heavy,...

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
        {"name": "SpaceX_list_rockets", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SpaceX_list_rockets"]
