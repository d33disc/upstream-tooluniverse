"""
LiteratureContextReviewer

Reviews coverage, relevance, and critical synthesis of prior scholarship.
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


def LiteratureContextReviewer(
    paper_title: str,
    literature_review: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Reviews coverage, relevance, and critical synthesis of prior scholarship.

    Parameters
    ----------
    paper_title : str

    literature_review : str
        Full literature-review text
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
            "name": "LiteratureContextReviewer",
            "arguments": {
                "paper_title": paper_title,
                "literature_review": literature_review,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LiteratureContextReviewer"]
