"""
AdverseEventICDMapper

Extracts adverse events from narrative clinical or pharmacovigilance text and maps each event to the most specific ICD-10-CM code.
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


def AdverseEventICDMapper(
    source_text: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Extracts adverse events from narrative clinical or pharmacovigilance text and maps each event to the most specific ICD-10-CM code.

    Parameters
    ----------
    source_text : str
        Unstructured narrative text that may mention adverse events.
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
        {"name": "AdverseEventICDMapper", "arguments": {"source_text": source_text}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AdverseEventICDMapper"]
