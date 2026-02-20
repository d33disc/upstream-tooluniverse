"""
NASATechPort_get_project

Get detailed information about a specific NASA TechPort technology project by its project ID. Ret...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def NASATechPort_get_project(
    project_id: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific NASA TechPort technology project by its project ID. Ret...

    Parameters
    ----------
    project_id : int
        TechPort project ID (e.g., 17792, 93217, 95645). Found via search results.
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
        {"name": "NASATechPort_get_project", "arguments": {"project_id": project_id}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NASATechPort_get_project"]
