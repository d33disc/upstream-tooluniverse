"""
FAERS_count_patient_age_distribution

Analyze the age distribution of patients experiencing adverse events for a specific drug. The age groups are: Neonate (0-28 days), Infant (29 days - 23 months), Child (2-11 years), Adolescent (12-17 years), Adult (18-64 years), Elderly (65+ years). Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_patient_age_distribution(
    medicinalproduct: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Analyze the age distribution of patients experiencing adverse events for a specific drug. The age groups are: Neonate (0-28 days), Infant (29 days - 23 months), Child (2-11 years), Adolescent (12-17 years), Adult (18-64 years), Elderly (65+ years). Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproduct : str
        Drug name.
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
            "name": "FAERS_count_patient_age_distribution",
            "arguments": {"medicinalproduct": medicinalproduct},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_patient_age_distribution"]
