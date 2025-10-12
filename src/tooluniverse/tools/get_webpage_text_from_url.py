"""
get_webpage_text_from_url

Render a URL as PDF and extract its text (JavaScript supported).
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


def get_webpage_text_from_url(
    url: str,
    timeout: Optional[int] = 30,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Render a URL as PDF and extract its text (JavaScript supported).

    Parameters
    ----------
    url : str
        Webpage URL to fetch and render
    timeout : int
        Request timeout in seconds
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
            "name": "get_webpage_text_from_url",
            "arguments": {"url": url, "timeout": timeout},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["get_webpage_text_from_url"]
