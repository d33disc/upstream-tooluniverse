"""
ToolGraphComposer

Builds a comprehensive graph of tool compatibility relationships in ToolUniverse. Analyzes all available tools and creates a directed graph showing which tools can be composed together.
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


def ToolGraphComposer(
    output_path: Optional[str] = "./tool_composition_graph",
    analysis_depth: Optional[str] = "detailed",
    min_compatibility_score: Optional[int] = 60,
    exclude_categories: Optional[list[Any]] = None,
    max_tools_per_category: Optional[int] = 50,
    force_rebuild: Optional[bool] = False,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Builds a comprehensive graph of tool compatibility relationships in ToolUniverse. Analyzes all available tools and creates a directed graph showing which tools can be composed together.

    Parameters
    ----------
    output_path : str
        Path to save the generated graph files (JSON and pickle formats)
    analysis_depth : str
        Level of compatibility analysis to perform
    min_compatibility_score : int
        Minimum compatibility score to create an edge in the graph
    exclude_categories : list[Any]
        Tool categories to exclude from analysis (e.g., ['tool_finder', 'special_tools'])
    max_tools_per_category : int
        Maximum number of tools to analyze per category (for performance)
    force_rebuild : bool
        Whether to force rebuild even if cached graph exists
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
    if exclude_categories is None:
        exclude_categories = ["tool_finder", "special_tools"]

    return _get_client().run_one_function(
        {
            "name": "ToolGraphComposer",
            "arguments": {
                "output_path": output_path,
                "analysis_depth": analysis_depth,
                "min_compatibility_score": min_compatibility_score,
                "exclude_categories": exclude_categories,
                "max_tools_per_category": max_tools_per_category,
                "force_rebuild": force_rebuild,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolGraphComposer"]
