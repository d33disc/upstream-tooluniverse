"""
NASATechPort_search_projects

Search NASA's TechPort database for technology development projects. TechPort catalogs NASA's tec...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASATechPort_search_projects(
    searchQuery: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search NASA's TechPort database for technology development projects. TechPort catalogs NASA's tec...

    Parameters
    ----------
    searchQuery : str
        Search query for NASA technology projects (e.g., 'mars rover', 'solar sail', ...
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
            "name": "NASATechPort_search_projects",
            "arguments": {"searchQuery": searchQuery},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASATechPort_search_projects"]
