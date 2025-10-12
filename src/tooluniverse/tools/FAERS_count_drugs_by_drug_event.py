"""
FAERS_count_drugs_by_drug_event

Count the number of different drugs involved in FDA adverse event reports, filtered by patient details, country, and seriousness. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_drugs_by_drug_event(
    patientsex: Optional[str] = None,
    patientagegroup: Optional[str] = None,
    occurcountry: Optional[str] = None,
    serious: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Count the number of different drugs involved in FDA adverse event reports, filtered by patient details, country, and seriousness. Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    patientsex : str
        Patient sex, leave it blank if you don't want to apply a filter.
    patientagegroup : str
        Patient age group.
    occurcountry : str
        Country where event occurred.
    serious : str
        Whether the event was serious.
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
            "name": "FAERS_count_drugs_by_drug_event",
            "arguments": {
                "patientsex": patientsex,
                "patientagegroup": patientagegroup,
                "occurcountry": occurcountry,
                "serious": serious,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_drugs_by_drug_event"]
