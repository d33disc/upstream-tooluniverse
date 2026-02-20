"""
MavenCentral_search_packages

Search Maven Central for Java/JVM packages (artifacts). Returns matching artifacts with groupId, ...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MavenCentral_search_packages(
    q: str,
    rows: Optional[int | Any] = None,
    start: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search Maven Central for Java/JVM packages (artifacts). Returns matching artifacts with groupId, ...

    Parameters
    ----------
    q : str
        Search query. Free text (e.g., 'spring boot') or Solr syntax: 'g:org.springfr...
    rows : int | Any
        Number of results to return (default 10, max 200)
    start : int | Any
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
            "name": "MavenCentral_search_packages",
            "arguments": {"q": q, "rows": rows, "start": start},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MavenCentral_search_packages"]
