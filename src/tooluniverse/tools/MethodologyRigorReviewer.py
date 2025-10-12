"""
MethodologyRigorReviewer

Evaluates design appropriateness, sampling, and procedural transparency.
"""

from typing import Any, Optional, Callable
from tooluniverse import ToolUniverse

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = ToolUniverse()
        _client.load_tools()
    return _client


def MethodologyRigorReviewer(
    methods_section: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Evaluates design appropriateness, sampling, and procedural transparency.

    Parameters
    ----------
    methods_section : str
        Full Methods text
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
    return _get_client().run_one_function(
        {
            "name": "MethodologyRigorReviewer",
            "arguments": {"methods_section": methods_section},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MethodologyRigorReviewer"]
