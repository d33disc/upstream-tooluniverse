"""
DockerHub_get_tags

Get available tags (versions) for a Docker Hub repository. Returns tag names with architecture de...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DockerHub_get_tags(
    namespace: str,
    page_size: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get available tags (versions) for a Docker Hub repository. Returns tag names with architecture de...

    Parameters
    ----------
    namespace : str
        Repository namespace and name. For official images: 'library/python', 'librar...
    page_size : int | Any
        Number of tags to return (default 10, max 100)
    page : int | Any
        Page number for pagination (default 1)
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
            "name": "DockerHub_get_tags",
            "arguments": {"namespace": namespace, "page_size": page_size, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DockerHub_get_tags"]
