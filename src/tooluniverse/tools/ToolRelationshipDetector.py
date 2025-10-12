"""
ToolRelationshipDetector

Analyzes a primary tool against a list of other tools to identify meaningful, directional data flow compatibilities for scientific workflows. Returns a list of compatible pairs with direction and rationale.
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


def ToolRelationshipDetector(
    tool_a: str,
    other_tools: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyzes a primary tool against a list of other tools to identify meaningful, directional data flow compatibilities for scientific workflows. Returns a list of compatible pairs with direction and rationale.

    Parameters
    ----------
    tool_a : str
        JSON string for the primary tool configuration (Tool A).
    other_tools : str
        JSON string of a list of other tool configurations to compare against Tool A.
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
            "name": "ToolRelationshipDetector",
            "arguments": {"tool_a": tool_a, "other_tools": other_tools},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolRelationshipDetector"]
