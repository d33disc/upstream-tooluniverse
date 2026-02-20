"""
OpenLibrary_get_work

Get detailed information about a literary work from Open Library by its work ID. A 'work' represe...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLibrary_get_work(
    work_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a literary work from Open Library by its work ID. A 'work' represe...

    Parameters
    ----------
    work_id : str
        Open Library work ID (e.g., 'OL27448W' for The Lord of the Rings, 'OL45804W' ...
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
        {"name": "OpenLibrary_get_work", "arguments": {"work_id": work_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLibrary_get_work"]
