"""
DescriptionQualityEvaluator

Evaluates the quality of tool descriptions and parameter descriptions, providing a score and specific feedback for improvements.
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


def DescriptionQualityEvaluator(
    tool_description: str,
    parameter_descriptions: str,
    test_results: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Evaluates the quality of tool descriptions and parameter descriptions, providing a score and specific feedback for improvements.

    Parameters
    ----------
    tool_description : str
        The tool description to evaluate.
    parameter_descriptions : str
        JSON string of parameter names and their descriptions.
    test_results : str
        JSON string containing test case results.
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
            "name": "DescriptionQualityEvaluator",
            "arguments": {
                "tool_description": tool_description,
                "parameter_descriptions": parameter_descriptions,
                "test_results": test_results,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DescriptionQualityEvaluator"]
