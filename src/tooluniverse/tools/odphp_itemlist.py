"""
odphp_itemlist

This tools browses and returns available topics and categories and it is helpful to help narrow a broad request (e.g., “show me all topics”). For full topic content, `odphp_topicsearch` tool is helpful.
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


def odphp_itemlist(
    lang: Optional[str] = None,
    type: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    This tools browses and returns available topics and categories and it is helpful to help narrow a broad request (e.g., “show me all topics”). For full topic content, `odphp_topicsearch` tool is helpful.

    Parameters
    ----------
    lang : str
        Language code (en or es)
    type : str
        topic or category
    stream_callback : Callable, optional
        Callback for streaming output
    use_cache : bool, default False
        Enable caching
    validate : bool, default True
        Validate parameters

    Returns
    -------
    dict[str, Any]
    """
    return _get_client().run_one_function(
        {"name": "odphp_itemlist", "arguments": {"lang": lang, "type": type}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["odphp_itemlist"]
