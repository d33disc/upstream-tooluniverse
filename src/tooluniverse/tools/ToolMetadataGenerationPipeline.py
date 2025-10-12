"""
ToolMetadataGenerationPipeline

Generates standardized metadata for a batch of ToolUniverse tool configurations by calling ToolMetadataGenerator, LabelGenerator, and ToolMetadataStandardizer for sources and tags.
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


def ToolMetadataGenerationPipeline(
    tool_configs: list[Any],
    tool_type_mappings: Optional[dict[str, Any]] = None,
    add_existing_tooluniverse_labels: Optional[bool] = True,
    max_new_tooluniverse_labels: Optional[int] = 0,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates standardized metadata for a batch of ToolUniverse tool configurations by calling ToolMetadataGenerator, LabelGenerator, and ToolMetadataStandardizer for sources and tags.

    Parameters
    ----------
    tool_configs : list[Any]
        List of raw tool configuration JSON objects to extract and standardize metadata for
    tool_type_mappings : dict[str, Any]
        Mapping of simplified toolType (keys) to lists of tool 'type' values belonging to each simplified category (e.g., {'Databases': ['XMLTool']})
    add_existing_tooluniverse_labels : bool
        Whether to include labels from existing ToolUniverse tools when labeling the metadata configs of the new tools. It is strongly recommended that this is set to true to minimize the number of new labels created and the possibility of redundant labels.
    max_new_tooluniverse_labels : int
        The maximum number of new ToolUniverse labels to use in the metadata configs of the new tools. The existing ToolUniverse labels will be used first, and then new labels will be created as needed up to this limit. If the limit is reached, the least relevant new labels will be discarded. Please try to use as few new labels as possible to avoid excessive labels.
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
    if tool_type_mappings is None:
        tool_type_mappings = {}

    return _get_client().run_one_function(
        {
            "name": "ToolMetadataGenerationPipeline",
            "arguments": {
                "tool_configs": tool_configs,
                "tool_type_mappings": tool_type_mappings,
                "add_existing_tooluniverse_labels": add_existing_tooluniverse_labels,
                "max_new_tooluniverse_labels": max_new_tooluniverse_labels,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolMetadataGenerationPipeline"]
