"""
DrugSafetyAnalyzer

Comprehensive drug safety analysis combining adverse event data, literature review, and molecular information
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


def DrugSafetyAnalyzer(
    drug_name: str,
    patient_sex: Optional[str] = None,
    serious_events_only: Optional[bool] = False,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Comprehensive drug safety analysis combining adverse event data, literature review, and molecular information

    Parameters
    ----------
    drug_name : str
        Name of the drug to analyze
    patient_sex : str
        Filter by patient sex (optional)
    serious_events_only : bool
        Focus only on serious adverse events
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
            "name": "DrugSafetyAnalyzer",
            "arguments": {
                "drug_name": drug_name,
                "patient_sex": patient_sex,
                "serious_events_only": serious_events_only,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["DrugSafetyAnalyzer"]
