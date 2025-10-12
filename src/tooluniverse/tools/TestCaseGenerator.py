"""
TestCaseGenerator

Generates diverse and representative ToolUniverse tool call dictionaries for a given tool based on its parameter schema. Each tool call should be a JSON object with 'name' (the tool's name) and 'arguments' (a dict of input arguments), covering different parameter combinations, edge cases, and typical usage. Can generate targeted test cases based on previous optimization feedback.
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


def TestCaseGenerator(
    tool_config: dict[str, Any],
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates diverse and representative ToolUniverse tool call dictionaries for a given tool based on its parameter schema. Each tool call should be a JSON object with 'name' (the tool's name) and 'arguments' (a dict of input arguments), covering different parameter combinations, edge cases, and typical usage. Can generate targeted test cases based on previous optimization feedback.

    Parameters
    ----------
    tool_config : dict[str, Any]
        The full configuration of the tool to generate test cases for. May include '_optimization_feedback' and '_iteration' fields for feedback-driven test generation.
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
        {"name": "TestCaseGenerator", "arguments": {"tool_config": tool_config}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["TestCaseGenerator"]
