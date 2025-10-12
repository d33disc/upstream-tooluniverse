"""
ToolOptimizer

Optimizes tool configurations based on quality feedback. Improves tool specifications and implementations to address identified issues.
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


def ToolOptimizer(
    tool_config: str,
    quality_feedback: str,
    optimization_target: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Optimizes tool configurations based on quality feedback. Improves tool specifications and implementations to address identified issues.

    Parameters
    ----------
    tool_config : str
        JSON string of the original tool configuration
    quality_feedback : str
        JSON string of quality evaluation feedback
    optimization_target : str
        What to optimize for (improve_quality, enhance_performance, etc.)
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
            "name": "ToolOptimizer",
            "arguments": {
                "tool_config": tool_config,
                "quality_feedback": quality_feedback,
                "optimization_target": optimization_target,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolOptimizer"]
