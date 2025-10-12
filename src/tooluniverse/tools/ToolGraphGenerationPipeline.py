"""
ToolGraphGenerationPipeline

Generates a directed tool relationship graph among provided tool configs using ToolRelationshipDetector to infer data-flow compatibility.
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


def ToolGraphGenerationPipeline(
    tool_configs: list[Any],
    max_tools: Optional[int] = None,
    output_path: Optional[str] = "./tool_relationship_graph.json",
    save_intermediate_every: Optional[int] = 5000,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates a directed tool relationship graph among provided tool configs using ToolRelationshipDetector to infer data-flow compatibility.

    Parameters
    ----------
    tool_configs : list[Any]
        List of tool configuration objects
    max_tools : int
        Optional max number of tools to process (debug)
    output_path : str
        Path for output graph JSON
    save_intermediate_every : int
        Checkpoint every N processed pairs
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
            "name": "ToolGraphGenerationPipeline",
            "arguments": {
                "tool_configs": tool_configs,
                "max_tools": max_tools,
                "output_path": output_path,
                "save_intermediate_every": save_intermediate_every,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolGraphGenerationPipeline"]
