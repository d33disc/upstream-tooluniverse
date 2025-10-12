"""
ToolCompatibilityAnalyzer

Analyzes two tool specifications to determine if one tool's output can be used as input for another tool. Returns compatibility information and suggested parameter mappings.
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


def ToolCompatibilityAnalyzer(
    source_tool: str,
    target_tool: str,
    analysis_depth: Optional[str] = "detailed",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyzes two tool specifications to determine if one tool's output can be used as input for another tool. Returns compatibility information and suggested parameter mappings.

    Parameters
    ----------
    source_tool : str
        The source tool specification (JSON string with name, description, parameter schema, and example outputs)
    target_tool : str
        The target tool specification (JSON string with name, description, parameter schema)
    analysis_depth : str
        Level of analysis depth - quick for basic compatibility, detailed for parameter mapping, comprehensive for semantic analysis
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
            "name": "ToolCompatibilityAnalyzer",
            "arguments": {
                "source_tool": source_tool,
                "target_tool": target_tool,
                "analysis_depth": analysis_depth,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolCompatibilityAnalyzer"]
