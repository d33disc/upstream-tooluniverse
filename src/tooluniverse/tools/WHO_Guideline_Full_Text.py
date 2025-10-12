"""
WHO_Guideline_Full_Text

Fetch full text content from a WHO (World Health Organization) guideline publication page. Extracts available web content and finds PDF download links. Use this after finding a guideline with WHO_Guidelines_Search to get the full content or PDF link.
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


def WHO_Guideline_Full_Text(
    url: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Fetch full text content from a WHO (World Health Organization) guideline publication page. Extracts available web content and finds PDF download links. Use this after finding a guideline with WHO_Guidelines_Search to get the full content or PDF link.

    Parameters
    ----------
    url : str
        Full URL of the WHO publication page (e.g., 'https://www.who.int/publications/i/item/9789240113879'). Must be a valid WHO publication URL.
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
        {"name": "WHO_Guideline_Full_Text", "arguments": {"url": url}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["WHO_Guideline_Full_Text"]
