"""
OpenLibrary_browse_subjects

Browse books by subject/topic from Open Library. Returns works filed under a given subject with t...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def OpenLibrary_browse_subjects(
    subject: str,
    limit: Optional[int | Any] = None,
    offset: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Browse books by subject/topic from Open Library. Returns works filed under a given subject with t...

    Parameters
    ----------
    subject : str
        Subject to browse. Use lowercase with underscores for multi-word subjects. Ex...
    limit : int | Any
        Number of works to return (default 12, max varies)
    offset : int | Any
        Offset for pagination (default 0)
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
            "name": "OpenLibrary_browse_subjects",
            "arguments": {"subject": subject, "limit": limit, "offset": offset},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["OpenLibrary_browse_subjects"]
