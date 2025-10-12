"""
AdverseEventPredictionQuestionGenerator

Generates a set of personalized adverse‐event prediction questions for a given disease and drug, across multiple patient subgroups.
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


def AdverseEventPredictionQuestionGenerator(
    disease_name: str,
    drug_name: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates a set of personalized adverse‐event prediction questions for a given disease and drug, across multiple patient subgroups.

    Parameters
    ----------
    disease_name : str
        The name of the disease or condition
    drug_name : str
        The name of the drug
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
            "name": "AdverseEventPredictionQuestionGenerator",
            "arguments": {"disease_name": disease_name, "drug_name": drug_name},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AdverseEventPredictionQuestionGenerator"]
