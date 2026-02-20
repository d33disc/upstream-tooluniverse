"""
ISS_get_astronauts

Get the current list of astronauts aboard the International Space Station (ISS) and other spacecr...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def ISS_get_astronauts(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the current list of astronauts aboard the International Space Station (ISS) and other spacecr...

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
        {"name": "ISS_get_astronauts", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ISS_get_astronauts"]
