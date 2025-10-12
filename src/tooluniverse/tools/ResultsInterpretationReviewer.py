"""
ResultsInterpretationReviewer

Judges whether conclusions are data-justified and limitations addressed.
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


def ResultsInterpretationReviewer(
    results_section: str,
    discussion_section: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Judges whether conclusions are data-justified and limitations addressed.

    Parameters
    ----------
    results_section : str

    discussion_section : str

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
            "name": "ResultsInterpretationReviewer",
            "arguments": {
                "results_section": results_section,
                "discussion_section": discussion_section,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ResultsInterpretationReviewer"]
