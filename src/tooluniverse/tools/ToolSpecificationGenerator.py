"""
ToolSpecificationGenerator

Generates complete ToolUniverse-compliant tool specifications based on a description and analysis of similar existing tools. Creates comprehensive tool configurations including parameters, prompts, and metadata.
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


def ToolSpecificationGenerator(
    tool_description: str,
    tool_category: str,
    tool_type: str,
    similar_tools: str,
    existing_tools_summary: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates complete ToolUniverse-compliant tool specifications based on a description and analysis of similar existing tools. Creates comprehensive tool configurations including parameters, prompts, and metadata.

    Parameters
    ----------
    tool_description : str
        Brief description of the desired tool functionality and purpose.
    tool_category : str
        Target category for the tool (e.g., 'biomedical', 'data_analysis', 'text_processing').
    tool_type : str
        Specific ToolUniverse tool type (e.g., 'AgenticTool', 'RESTTool', 'PythonTool').
    similar_tools : str
        JSON string containing configurations of similar existing tools for analysis and differentiation.
    existing_tools_summary : str
        Summary of existing tools in the ecosystem to avoid duplication and identify gaps.
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
            "name": "ToolSpecificationGenerator",
            "arguments": {
                "tool_description": tool_description,
                "tool_category": tool_category,
                "tool_type": tool_type,
                "similar_tools": similar_tools,
                "existing_tools_summary": existing_tools_summary,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolSpecificationGenerator"]
