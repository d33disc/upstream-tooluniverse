"""
LiteratureSearchTool

Comprehensive literature search and summary tool that searches multiple databases (EuropePMC, OpenAlex, PubTator) and generates AI-powered summaries of research findings
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


def LiteratureSearchTool(
    research_topic: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Comprehensive literature search and summary tool that searches multiple databases (EuropePMC, OpenAlex, PubTator) and generates AI-powered summaries of research findings

    Parameters
    ----------
    research_topic : str
        The research topic or query to search for in the literature
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
            "name": "LiteratureSearchTool",
            "arguments": {"research_topic": research_topic},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["LiteratureSearchTool"]
