"""
ToolOutputSummarizer

AI-powered tool for summarizing long tool outputs, focusing on key information relevant to the original query
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


def ToolOutputSummarizer(
    tool_output: str,
    query_context: str,
    tool_name: str,
    focus_areas: Optional[str] = "key_findings_and_results",
    max_length: Optional[int] = 32000,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    AI-powered tool for summarizing long tool outputs, focusing on key information relevant to the original query

    Parameters
    ----------
    tool_output : str
        The original tool output to be summarized
    query_context : str
        Context about the original query that triggered the tool
    tool_name : str
        Name of the tool that generated the output
    focus_areas : str
        Specific areas to focus on in the summary
    max_length : int
        Maximum length of the summary in characters
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
            "name": "ToolOutputSummarizer",
            "arguments": {
                "tool_output": tool_output,
                "query_context": query_context,
                "tool_name": tool_name,
                "focus_areas": focus_areas,
                "max_length": max_length,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ToolOutputSummarizer"]
