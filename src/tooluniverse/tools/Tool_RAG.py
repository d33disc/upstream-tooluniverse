"""
Tool_RAG

Retrieve related tools from the toolbox based on the provided description
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


def Tool_RAG(
    description: Optional[str] = None,
    limit: Optional[int] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Retrieve related tools from the toolbox based on the provided description

    Parameters
    ----------
    description : str
        The description of the tool capability required.
    limit : int
        The number of tools to retrieve
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
        {"name": "Tool_RAG", "arguments": {"description": description, "limit": limit}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["Tool_RAG"]
