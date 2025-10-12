"""
LabelGenerator

Generates relevant keyword labels for tools based on their name, description, parameters, and category. Creates a comprehensive list of tags for tool discovery and categorization.
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


def LabelGenerator(
    tool_name: str,
    tool_description: str,
    tool_parameters: str,
    category: str,
    existing_labels: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates relevant keyword labels for tools based on their name, description, parameters, and category. Creates a comprehensive list of tags for tool discovery and categorization.

    Parameters
    ----------
    tool_name : str
        The name of the tool
    tool_description : str
        Detailed description of what the tool does
    tool_parameters : str
        JSON string describing the tool's input parameters and their types
    category : str
        The general category or domain the tool belongs to
    existing_labels : str
        JSON array string of existing labels to consider reusing (optional)
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
            "name": "LabelGenerator",
            "arguments": {
                "tool_name": tool_name,
                "tool_description": tool_description,
                "tool_parameters": tool_parameters,
                "category": category,
                "existing_labels": existing_labels,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LabelGenerator"]
