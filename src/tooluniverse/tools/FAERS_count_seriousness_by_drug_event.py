"""
FAERS_count_seriousness_by_drug_event

Count the number of adverse event reports classified as serious or non-serious, filtered by drug and patient demographics. In results, term Serious means: 'The adverse event resulted in death, a life threatening condition, hospitalization, disability, congenital anomaly, or other serious condition', term Non-serious means 'The adverse event did not result in any of the above' Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_seriousness_by_drug_event(
    medicinalproduct: Optional[str] = None,
    patientsex: Optional[str] = None,
    patientagegroup: Optional[str] = None,
    occurcountry: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Count the number of adverse event reports classified as serious or non-serious, filtered by drug and patient demographics. In results, term Serious means: 'The adverse event resulted in death, a life threatening condition, hospitalization, disability, congenital anomaly, or other serious condition', term Non-serious means 'The adverse event did not result in any of the above' Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproduct : str
        Drug name.
    patientsex : str
        Patient sex, leave it blank if you don't want to apply a filter.
    patientagegroup : str
        Patient age group.
    occurcountry : str
        Country where event occurred.
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
            "name": "FAERS_count_seriousness_by_drug_event",
            "arguments": {
                "medicinalproduct": medicinalproduct,
                "patientsex": patientsex,
                "patientagegroup": patientagegroup,
                "occurcountry": occurcountry,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_seriousness_by_drug_event"]
