"""
ToolMetadataStandardizer

Standardizes and groups semantically equivalent metadata strings (e.g., sources, tags) into canonical forms for consistent downstream usage.
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


def ToolMetadataStandardizer(
    metadata_list: list[Any],
    limit: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Standardizes and groups semantically equivalent metadata strings (e.g., sources, tags) into canonical forms for consistent downstream usage.

    Parameters
    ----------
    metadata_list : list[Any]
        List of raw metadata strings (e.g., sources, tags) to standardize and group.
    limit : int
        If provided, the maximum number of canonical strings to return. The LLM will group terms more aggressively to meet this limit, ensuring all raw strings are mapped.
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
            "name": "ToolMetadataStandardizer",
            "arguments": {"metadata_list": metadata_list, "limit": limit},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolMetadataStandardizer"]
