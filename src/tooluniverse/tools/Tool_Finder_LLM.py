"""
Tool_Finder_LLM

LLM-based tool finder that uses natural language processing to intelligently select relevant tools based on user queries. This tool analyzes all available tool descriptions and uses an LLM to determine which tools would be most helpful for a given task or question.
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


def Tool_Finder_LLM(
    description: str,
    limit: int,
    picked_tool_names: Optional[list[Any]] = None,
    return_call_result: Optional[bool] = None,
    categories: Optional[list[Any]] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    LLM-based tool finder that uses natural language processing to intelligently select relevant tools based on user queries. This tool analyzes all available tool descriptions and uses an LLM to determine which tools would be most helpful for a given task or question.

    Parameters
    ----------
    description : str
        The description of the tool capability required.
    limit : int
        The number of tools to retrieve
    picked_tool_names : list[Any]
        Pre-selected tool names to process. If provided, tool selection will skip these tools.
    return_call_result : bool
        Whether to return both prompts and tool names. If false, returns only tool prompts.
    categories : list[Any]
        Optional list of tool categories to filter by
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
            "name": "Tool_Finder_LLM",
            "arguments": {
                "description": description,
                "limit": limit,
                "picked_tool_names": picked_tool_names,
                "return_call_result": return_call_result,
                "categories": categories,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Tool_Finder_LLM"]
