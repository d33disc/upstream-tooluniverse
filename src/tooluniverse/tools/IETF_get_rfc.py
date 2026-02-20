"""
IETF_get_rfc

Get detailed information about a specific RFC (Request for Comments) document from the IETF Datat...
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def IETF_get_rfc(
    rfc_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Get detailed information about a specific RFC (Request for Comments) document from the IETF Datat...

    Parameters
    ----------
    rfc_name : str
        RFC document name in format 'rfcNNNN'. Examples: 'rfc9110' (HTTP Semantics), ...
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
        {"name": "IETF_get_rfc", "arguments": {"rfc_name": rfc_name}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["IETF_get_rfc"]
