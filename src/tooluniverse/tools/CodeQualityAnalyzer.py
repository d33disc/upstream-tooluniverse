"""
CodeQualityAnalyzer

Analyzes code quality from multiple dimensions including algorithmic correctness, functional implementation capability, performance characteristics, and best practices. Provides detailed feedback and improvement suggestions.
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


def CodeQualityAnalyzer(
    tool_name: str,
    tool_description: str,
    tool_parameters: str,
    implementation_code: str,
    test_cases: str,
    test_execution_results: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyzes code quality from multiple dimensions including algorithmic correctness, functional implementation capability, performance characteristics, and best practices. Provides detailed feedback and improvement suggestions.

    Parameters
    ----------
    tool_name : str
        Name of the tool being analyzed
    tool_description : str
        Description of what the tool is supposed to do
    tool_parameters : str
        JSON string of tool parameters and their types
    implementation_code : str
        The actual implementation code to analyze
    test_cases : str
        JSON string of test cases for the tool
    test_execution_results : str
        JSON string of test execution results including pass/fail status and actual outputs
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
            "name": "CodeQualityAnalyzer",
            "arguments": {
                "tool_name": tool_name,
                "tool_description": tool_description,
                "tool_parameters": tool_parameters,
                "implementation_code": implementation_code,
                "test_cases": test_cases,
                "test_execution_results": test_execution_results,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["CodeQualityAnalyzer"]
