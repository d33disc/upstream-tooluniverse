"""
VAM_get_object

Get detailed information about a specific Victoria and Albert Museum object by its system number....
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def VAM_get_object(
    objectId: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific Victoria and Albert Museum object by its system number....

    Parameters
    ----------
    objectId : str
        V&A system number (e.g. 'O142600', 'O105780'). Obtained from VAM_search_objec...
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
        {"name": "VAM_get_object", "arguments": {"objectId": objectId}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["VAM_get_object"]
