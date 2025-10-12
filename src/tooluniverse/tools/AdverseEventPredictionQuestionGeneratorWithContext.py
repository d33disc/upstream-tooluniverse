"""
AdverseEventPredictionQuestionGeneratorWithContext

Generates a set of personalized adverse‐event prediction questions for a given disease and drug, incorporating additional context information such as patient medical history, clinical findings, or research data.
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


def AdverseEventPredictionQuestionGeneratorWithContext(
    disease_name: str,
    drug_name: str,
    context_information: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Generates a set of personalized adverse‐event prediction questions for a given disease and drug, incorporating additional context information such as patient medical history, clinical findings, or research data.

    Parameters
    ----------
    disease_name : str
        The name of the disease or condition
    drug_name : str
        The name of the drug
    context_information : str
        Additional context information such as patient medical history, clinical findings, research data, or other relevant background information that should inform the adverse event prediction questions
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
            "name": "AdverseEventPredictionQuestionGeneratorWithContext",
            "arguments": {
                "disease_name": disease_name,
                "drug_name": drug_name,
                "context_information": context_information,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["AdverseEventPredictionQuestionGeneratorWithContext"]
