"""
Cataas_get_tags

Get all available cat image tags from the Cat as a Service (CATAAS) API. Returns the complete lis...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def Cataas_get_tags(
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get all available cat image tags from the Cat as a Service (CATAAS) API. Returns the complete lis...

    Parameters
    ----------
    No parameters
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
        {"name": "Cataas_get_tags", "arguments": {}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Cataas_get_tags"]
