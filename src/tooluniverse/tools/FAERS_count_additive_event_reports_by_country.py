"""
FAERS_count_additive_event_reports_by_country

Additive multi-drug data: Aggregate report counts by country of occurrence across specified medicinal products. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_additive_event_reports_by_country(
    medicinalproducts: list[Any],
    patientsex: Optional[str] = None,
    patientagegroup: Optional[str] = None,
    serious: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Additive multi-drug data: Aggregate report counts by country of occurrence across specified medicinal products. Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproducts : list[Any]
        Array of medicinal product names.
    patientsex : str
        Filter by sex.
    patientagegroup : str
        Filter by age group.
    serious : str
        Filter by seriousness.
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
            "name": "FAERS_count_additive_event_reports_by_country",
            "arguments": {
                "medicinalproducts": medicinalproducts,
                "patientsex": patientsex,
                "patientagegroup": patientagegroup,
                "serious": serious,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_additive_event_reports_by_country"]
