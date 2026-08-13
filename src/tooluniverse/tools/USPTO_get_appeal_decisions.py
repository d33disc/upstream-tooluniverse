"""
USPTO_get_appeal_decisions

Get all decisions filed in a PTAB appeal by appeal number.
"""

from typing import Any, Optional, Callable
from ._shared_client import get_shared_client


def USPTO_get_appeal_decisions(
    appealNumber: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Get all decisions filed in a PTAB appeal by appeal number.

    Parameters
    ----------
    appealNumber : str

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
    _args = {k: v for k, v in {"appealNumber": appealNumber}.items() if v is not None}
    return get_shared_client().run_one_function(
        {
            "name": "USPTO_get_appeal_decisions",
            "arguments": _args,
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["USPTO_get_appeal_decisions"]
