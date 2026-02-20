"""
DockerHub_search_repositories

Search Docker Hub for container image repositories. Returns matching repositories with name, desc...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def DockerHub_search_repositories(
    query: str,
    page_size: Optional[int | Any] = None,
    page: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Docker Hub for container image repositories. Returns matching repositories with name, desc...

    Parameters
    ----------
    query : str
        Search query (e.g., 'python', 'nginx', 'postgres', 'bioinformatics', 'jupyter')
    page_size : int | Any
        Number of results per page (default 25, max 100)
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
            "name": "DockerHub_search_repositories",
            "arguments": {"query": query, "page_size": page_size, "page": page},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DockerHub_search_repositories"]
