"""
OpenLibrary_get_author

Get detailed information about an author from Open Library by their author ID. Returns the author...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLibrary_get_author(
    author_id: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about an author from Open Library by their author ID. Returns the author...

    Parameters
    ----------
    author_id : str
        Open Library author ID (e.g., 'OL26320A' for J.R.R. Tolkien, 'OL34184A' for R...
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
        {"name": "OpenLibrary_get_author", "arguments": {"author_id": author_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLibrary_get_author"]
