"""
MedicalTermNormalizer

Identifies and corrects misspelled drug or disease names, returning a list of plausible standardized terms.
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


def MedicalTermNormalizer(
    raw_terms: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Identifies and corrects misspelled drug or disease names, returning a list of plausible standardized terms.

    Parameters
    ----------
    raw_terms : str
        A comma- or whitespace-separated string containing one misspelled drug or disease name.
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
        {"name": "MedicalTermNormalizer", "arguments": {"raw_terms": raw_terms}},
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["MedicalTermNormalizer"]
