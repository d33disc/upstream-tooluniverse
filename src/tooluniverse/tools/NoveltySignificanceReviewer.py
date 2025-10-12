"""
NoveltySignificanceReviewer

Provides a structured peer-review of the work's originality and potential impact.
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


def NoveltySignificanceReviewer(
    paper_title: str,
    abstract: str,
    manuscript_text: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Provides a structured peer-review of the work's originality and potential impact.

    Parameters
    ----------
    paper_title : str
        Manuscript title
    abstract : str
        Manuscript abstract
    manuscript_text : str
        Full manuscript text
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
            "name": "NoveltySignificanceReviewer",
            "arguments": {
                "paper_title": paper_title,
                "abstract": abstract,
                "manuscript_text": manuscript_text,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["NoveltySignificanceReviewer"]
