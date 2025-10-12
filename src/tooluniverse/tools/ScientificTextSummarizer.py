"""
ScientificTextSummarizer

Summarizes biomedical research texts, abstracts, or papers with specified length and focus areas. Uses AI to extract key findings, methodology, and conclusions from complex biomedical literature.
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


def ScientificTextSummarizer(
    text: str,
    summary_length: str,
    focus_area: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Summarizes biomedical research texts, abstracts, or papers with specified length and focus areas. Uses AI to extract key findings, methodology, and conclusions from complex biomedical literature.

    Parameters
    ----------
    text : str
        The biomedical text, abstract, or paper content to be summarized.
    summary_length : str
        Desired length of summary (e.g., '50', '100', '200 words').
    focus_area : str
        What to focus on in the summary (e.g., 'methodology', 'results', 'clinical implications', 'drug interactions').
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
            "name": "ScientificTextSummarizer",
            "arguments": {
                "text": text,
                "summary_length": summary_length,
                "focus_area": focus_area,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["ScientificTextSummarizer"]
