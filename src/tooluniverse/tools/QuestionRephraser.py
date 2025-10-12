"""
QuestionRephraser

Generates three distinct paraphrases of a given question while ensuring answer options remain valid and applicable.
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


def QuestionRephraser(
    question: str,
    options: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates three distinct paraphrases of a given question while ensuring answer options remain valid and applicable.

    Parameters
    ----------
    question : str
        The original question text to be rephrased
    options : str
        Answer options (e.g., multiple choice options) that should remain valid for the rephrased questions. Leave empty if no options are provided.
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
            "name": "QuestionRephraser",
            "arguments": {"question": question, "options": options},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["QuestionRephraser"]
