"""
ToolDiscover

Generates new ToolUniverse-compliant tools based on short descriptions through an intelligent discovery and refinement process. Automatically determines the optimal tool type and category, discovers similar existing tools, generates initial specifications, and iteratively refines the tool configuration using agentic optimization tools until it meets quality standards.
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


def ToolDiscover(
    tool_description: str,
    max_iterations: Optional[int] = 20,
    save_to_file: Optional[bool] = True,
    output_file: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates new ToolUniverse-compliant tools based on short descriptions through an intelligent discovery and refinement process. Automatically determines the optimal tool type and category, discovers similar existing tools, generates initial specifications, and iteratively refines the tool configuration using agentic optimization tools until it meets quality standards.

    Parameters
    ----------
    tool_description : str
        Short description of the desired tool functionality and purpose. Tool Discover will automatically analyze this to determine the optimal tool type (PackageTool, RESTTool, XMLTool, or AgenticTool) and appropriate category.
    max_iterations : int
        Maximum number of refinement iterations to perform.
    save_to_file : bool
        Whether to save the generated tool configuration and report to a file.
    output_file : str
        Optional file path to save the generated tool. If not provided, uses auto-generated filename.
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
            "name": "ToolDiscover",
            "arguments": {
                "tool_description": tool_description,
                "max_iterations": max_iterations,
                "save_to_file": save_to_file,
                "output_file": output_file,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolDiscover"]
