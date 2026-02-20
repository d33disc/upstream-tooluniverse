"""
MavenCentral_get_package_versions

Get the version history of a specific Maven artifact from Maven Central. Pass the groupId and art...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MavenCentral_get_package_versions(
    q: str,
    rows: Optional[int | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get the version history of a specific Maven artifact from Maven Central. Pass the groupId and art...

    Parameters
    ----------
    q : str
        Solr query for specific artifact: 'g:{groupId} AND a:{artifactId}' (e.g., 'g:...
    rows : int | Any
        Number of versions to return (default 10, max 200)
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
            "name": "MavenCentral_get_package_versions",
            "arguments": {"q": q, "rows": rows},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MavenCentral_get_package_versions"]
