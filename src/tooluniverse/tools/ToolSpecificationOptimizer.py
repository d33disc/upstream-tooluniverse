"""
ToolSpecificationOptimizer

Optimizes tool specifications for clarity, completeness, and usability with comprehensive benchmarking against similar tools
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


def ToolSpecificationOptimizer(
    tool_config: str,
    optimization_focus: Optional[str] = "all",
    target_audience: Optional[str] = "mixed",
    similar_tools: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Optimizes tool specifications for clarity, completeness, and usability with comprehensive benchmarking against similar tools

    Parameters
    ----------
    tool_config : str
        JSON string of current tool configuration to optimize
    optimization_focus : str
        Primary optimization focus
    target_audience : str
        Target user expertise level
    similar_tools : str
        JSON string array of similar tools for comparison and benchmarking
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
            "name": "ToolSpecificationOptimizer",
            "arguments": {
                "tool_config": tool_config,
                "optimization_focus": optimization_focus,
                "target_audience": target_audience,
                "similar_tools": similar_tools,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolSpecificationOptimizer"]
