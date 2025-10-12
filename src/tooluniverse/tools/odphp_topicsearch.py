"""
odphp_topicsearch

Find specific health topics and get their full content. Use when the user mentions a keyword (e.g., “folic acid”, “blood pressure”) or when you already have topic/category IDs from `odphp_itemlist`. Returns detailed topic pages (Title, Sections, RelatedItems) and an AccessibleVersion link. Next: to quote or summarize the actual page text, pass the AccessibleVersion (or RelatedItems URLs) to `odphp_outlink_fetch`.
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


def odphp_topicsearch(
    lang: Optional[str] = None,
    topicId: Optional[str] = None,
    categoryId: Optional[str] = None,
    keyword: Optional[str] = None,
    strip_html: Optional[bool] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> dict[str, Any]:
    """
    Find specific health topics and get their full content. Use when the user mentions a keyword (e.g., “folic acid”, “blood pressure”) or when you already have topic/category IDs from `odphp_itemlist`. Returns detailed topic pages (Title, Sections, RelatedItems) and an AccessibleVersion link. Next: to quote or summarize the actual page text, pass the AccessibleVersion (or RelatedItems URLs) to `odphp_outlink_fetch`.

    Parameters
    ----------
    lang : str
        Language code (en or es)
    topicId : str
        Comma-separated topic IDs
    categoryId : str
        Comma-separated category IDs
    keyword : str
        Keyword search for topics
    strip_html : bool
        If true, also return PlainSections[] with HTML removed for each topic
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
            "name": "odphp_topicsearch",
            "arguments": {
                "lang": lang,
                "topicId": topicId,
                "categoryId": categoryId,
                "keyword": keyword,
                "strip_html": strip_html,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["odphp_topicsearch"]
