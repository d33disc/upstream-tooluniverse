"""
USPTO_download_interference_decisions

Download PTAB interference decision search results as CSV or JSON.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def USPTO_download_interference_decisions(
    q: str,
    format: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Download PTAB interference decision search results as CSV or JSON.

    Parameters
    ----------
    q : str

    format : str

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
    _args = {k: v for k, v in {"q": q, "format": format}.items() if v is not None}
    return get_shared_client().run_one_function(
        {
            "name": "USPTO_download_interference_decisions",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["USPTO_download_interference_decisions"]
