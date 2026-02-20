"""
MetMuseum_get_object

Get detailed information about a specific Metropolitan Museum of Art artwork or artifact by its o...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def MetMuseum_get_object(
    objectID: int,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific Metropolitan Museum of Art artwork or artifact by its o...

    Parameters
    ----------
    objectID : int
        The Met object ID number (obtained from MetMuseum_search_objects). Example: 4...
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
        {"name": "MetMuseum_get_object", "arguments": {"objectID": objectID}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MetMuseum_get_object"]
