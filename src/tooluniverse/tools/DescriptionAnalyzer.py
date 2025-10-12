"""
DescriptionAnalyzer

Analyzes a tool's original description and the results of multiple test cases, then suggests an improved description that is more accurate, comprehensive, and user-friendly. Optionally provides a rationale for the changes.
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


def DescriptionAnalyzer(
    original_description: str,
    test_results: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyzes a tool's original description and the results of multiple test cases, then suggests an improved description that is more accurate, comprehensive, and user-friendly. Optionally provides a rationale for the changes.

    Parameters
    ----------
    original_description : str
        The original description of the tool.
    test_results : str
        A JSON string containing a list of test case input/output pairs.
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
            "name": "DescriptionAnalyzer",
            "arguments": {
                "original_description": original_description,
                "test_results": test_results,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DescriptionAnalyzer"]
