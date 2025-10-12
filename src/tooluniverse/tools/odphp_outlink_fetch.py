"""
odphp_outlink_fetch

This tool retrieves readable text from ODPHP article links and information sources. This is helpful after using the `odphp_myhealthfinder` or `odphp_topicsearch` tools or when the user wants to simply dive deeper into ODPHP data.
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


def odphp_outlink_fetch(
    urls: list[Any],
    max_chars: Optional[int] = None,
    return_html: Optional[bool] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    This tool retrieves readable text from ODPHP article links and information sources. This is helpful after using the `odphp_myhealthfinder` or `odphp_topicsearch` tools or when the user wants to simply dive deeper into ODPHP data.

    Parameters
    ----------
    urls : list[Any]
        1–3 absolute URLs from AccessibleVersion or RelatedItems.Url
    max_chars : int
        Optional hard cap on extracted text length (e.g., 5000)
    return_html : bool
        If true, also return minimally cleaned HTML
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
        {
            "name": "odphp_outlink_fetch",
            "arguments": {
                "urls": urls,
                "max_chars": max_chars,
                "return_html": return_html,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["odphp_outlink_fetch"]
