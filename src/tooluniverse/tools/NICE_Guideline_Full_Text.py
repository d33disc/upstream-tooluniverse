"""
NICE_Guideline_Full_Text

Fetch complete full text content from a NICE clinical guideline page. Takes a NICE guideline URL and extracts all sections, recommendations, and complete guideline text. Use this after finding a guideline with NICE_Clinical_Guidelines_Search to get the full content.
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


def NICE_Guideline_Full_Text(
    url: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Fetch complete full text content from a NICE clinical guideline page. Takes a NICE guideline URL and extracts all sections, recommendations, and complete guideline text. Use this after finding a guideline with NICE_Clinical_Guidelines_Search to get the full content.

    Parameters
    ----------
    url : str
        Full URL of the NICE guideline page (e.g., 'https://www.nice.org.uk/guidance/ng28'). Must be a valid NICE guideline URL.
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
        {"name": "NICE_Guideline_Full_Text", "arguments": {"url": url}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NICE_Guideline_Full_Text"]
