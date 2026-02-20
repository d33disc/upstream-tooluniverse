"""
npm_get_package

Get detailed metadata for a specific npm package including all versions, dependencies, repository...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def npm_get_package(
    package: str,
    version: Optional[str | Any] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed metadata for a specific npm package including all versions, dependencies, repository...

    Parameters
    ----------
    package : str
        npm package name (case-sensitive for scoped packages). Examples: 'react', 'd3...
    version : str | Any
        Specific version to get. If null, returns the 'latest' tagged version. Exampl...
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
            "name": "npm_get_package",
            "arguments": {"package": package, "version": version},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["npm_get_package"]
