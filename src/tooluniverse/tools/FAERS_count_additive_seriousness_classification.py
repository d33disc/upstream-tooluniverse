"""
FAERS_count_additive_seriousness_classification

Additive multi-drug data: Quantify serious vs non-serious classifications across medicinal products, annotated per regulatory definitions. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_additive_seriousness_classification(
    medicinalproducts: list[Any],
    patientsex: Optional[str] = None,
    patientagegroup: Optional[str] = None,
    occurcountry: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Additive multi-drug data: Quantify serious vs non-serious classifications across medicinal products, annotated per regulatory definitions. Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproducts : list[Any]
        Array of medicinal product names.
    patientsex : str
        Filter by sex.
    patientagegroup : str
        Filter by age group.
    occurcountry : str
        ISO2 country code filter.
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
            "name": "FAERS_count_additive_seriousness_classification",
            "arguments": {
                "medicinalproducts": medicinalproducts,
                "patientsex": patientsex,
                "patientagegroup": patientagegroup,
                "occurcountry": occurcountry,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_additive_seriousness_classification"]
