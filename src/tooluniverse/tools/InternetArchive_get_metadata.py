"""
InternetArchive_get_metadata

Get full metadata for a specific Internet Archive item by its identifier. Returns comprehensive m...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def InternetArchive_get_metadata(
    identifier: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get full metadata for a specific Internet Archive item by its identifier. Returns comprehensive m...

    Parameters
    ----------
    identifier : str
        Internet Archive item identifier (e.g., 'ibda3gate.comlearnpythonprogrammingl...
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
        {
            "name": "InternetArchive_get_metadata",
            "arguments": {"identifier": identifier},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["InternetArchive_get_metadata"]
