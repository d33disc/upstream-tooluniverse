"""
SpaceX_get_rocket

Get detailed specifications for a specific SpaceX rocket by ID. Returns dimensions, mass, payload...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def SpaceX_get_rocket(
    rocket_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed specifications for a specific SpaceX rocket by ID. Returns dimensions, mass, payload...

    Parameters
    ----------
    rocket_id : str
        SpaceX rocket ID (e.g., '5e9d0d95eda69973a809d1ec' for Falcon 9)
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
        {"name": "SpaceX_get_rocket", "arguments": {"rocket_id": rocket_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["SpaceX_get_rocket"]
