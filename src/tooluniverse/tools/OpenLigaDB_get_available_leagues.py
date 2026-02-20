"""
OpenLigaDB_get_available_leagues

Get a list of all available leagues and seasons in OpenLigaDB. Returns league names, shortcut cod...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLigaDB_get_available_leagues(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get a list of all available leagues and seasons in OpenLigaDB. Returns league names, shortcut cod...

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
        {"name": "OpenLigaDB_get_available_leagues", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLigaDB_get_available_leagues"]
