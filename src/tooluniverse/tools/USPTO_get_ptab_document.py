"""
USPTO_get_ptab_document

Get a PTAB trial document by document identifier.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def USPTO_get_ptab_document(
    documentIdentifier: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get a PTAB trial document by document identifier.

    Parameters
    ----------
    documentIdentifier : str

    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    # Handle mutable defaults to avoid B006 linting error

    # Strip None values so optional parameters don't trigger schema validation errors
    _args = {
        k: v
        for k, v in {"documentIdentifier": documentIdentifier}.items()
        if v is not None
    }
    return get_shared_client().run_one_function(
        {
            "name": "USPTO_get_ptab_document",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["USPTO_get_ptab_document"]
