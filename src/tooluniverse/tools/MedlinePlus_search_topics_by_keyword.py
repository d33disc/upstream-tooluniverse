"""
MedlinePlus_search_topics_by_keyword

Search for relevant information in MedlinePlus Web Service by keyword across health topics or other sub-libraries (such as drugs, genetics, etc.).
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


def MedlinePlus_search_topics_by_keyword(
    term: str,
    db: str,
    rettype: Optional[str] = "topic",
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Search for relevant information in MedlinePlus Web Service by keyword across health topics or other sub-libraries (such as drugs, genetics, etc.).

    Parameters
    ----------
    term : str
        Search keyword, e.g., "diabetes", needs to be URL encoded before passing.
    db : str
        Specify the database to search, e.g., healthTopics (English health topics), healthTopicsSpanish (Spanish health topics), drugs (English drugs), etc.
    rettype : str
        Result return format, options: brief (concise information, default), topic (detailed XML record), all (includes all available information).
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
            "name": "MedlinePlus_search_topics_by_keyword",
            "arguments": {"term": term, "db": db, "rettype": rettype},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MedlinePlus_search_topics_by_keyword"]
