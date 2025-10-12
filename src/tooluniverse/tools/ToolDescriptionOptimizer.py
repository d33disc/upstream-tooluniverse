"""
ToolDescriptionOptimizer

Optimizes a tool's description and parameter descriptions by generating test cases, executing them, analyzing the results, and suggesting improved descriptions for both the tool and its arguments. Optionally saves a comprehensive optimization report to a file without overwriting the original.
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


def ToolDescriptionOptimizer(
    tool_config: dict[str, Any],
    save_to_file: Optional[bool] = False,
    output_file: Optional[str] = None,
    max_iterations: Optional[int] = 3,
    satisfaction_threshold: Optional[float] = 8,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Optimizes a tool's description and parameter descriptions by generating test cases, executing them, analyzing the results, and suggesting improved descriptions for both the tool and its arguments. Optionally saves a comprehensive optimization report to a file without overwriting the original.

    Parameters
    ----------
    tool_config : dict[str, Any]
        The full configuration of the tool to optimize.
    save_to_file : bool
        If true, save the optimized description to a file (do not overwrite the original).
    output_file : str
        Optional file path to save the optimized description. If not provided, use '<tool_name>_optimized_description.txt'.
    max_iterations : int
        Maximum number of optimization rounds to perform.
    satisfaction_threshold : float
        Quality score threshold (1-10) to consider optimization satisfactory.
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
            "name": "ToolDescriptionOptimizer",
            "arguments": {
                "tool_config": tool_config,
                "save_to_file": save_to_file,
                "output_file": output_file,
                "max_iterations": max_iterations,
                "satisfaction_threshold": satisfaction_threshold,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolDescriptionOptimizer"]
