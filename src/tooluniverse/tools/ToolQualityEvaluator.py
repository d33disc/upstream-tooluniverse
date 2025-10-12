"""
ToolQualityEvaluator

Evaluates the quality of tool configurations and implementations. Provides detailed scoring and feedback for improvement.
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


def ToolQualityEvaluator(
    tool_config: str,
    test_cases: Optional[str] = None,
    evaluation_aspects: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Evaluates the quality of tool configurations and implementations. Provides detailed scoring and feedback for improvement.

    Parameters
    ----------
    tool_config : str
        JSON string of the tool configuration
    test_cases : str
        JSON string of test cases
    evaluation_aspects : list[Any]
        Aspects to evaluate (functionality, usability, completeness, best_practices)
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
            "name": "ToolQualityEvaluator",
            "arguments": {
                "tool_config": tool_config,
                "test_cases": test_cases,
                "evaluation_aspects": evaluation_aspects,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolQualityEvaluator"]
