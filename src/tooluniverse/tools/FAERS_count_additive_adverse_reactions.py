"""
FAERS_count_additive_adverse_reactions

Additive multi-drug data: Aggregate adverse reaction counts across specified medicinal products, stratified by demographics, seriousness, and outcomes. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_additive_adverse_reactions(
    medicinalproducts: list[Any],
    patientsex: Optional[str] = None,
    patientagegroup: Optional[str] = None,
    occurcountry: Optional[str] = None,
    serious: Optional[str] = None,
    seriousnessdeath: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Additive multi-drug data: Aggregate adverse reaction counts across specified medicinal products, stratified by demographics, seriousness, and outcomes. Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproducts : list[Any]
        Array of medicinal product names.
    patientsex : str
        Filter by patient sex.
    patientagegroup : str
        Filter by patient age group.
    occurcountry : str
        Filter by ISO2 country code of occurrence.
    serious : str
        Filter by seriousness classification.
    seriousnessdeath : str
        Filter for fatal outcomes.
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
            "name": "FAERS_count_additive_adverse_reactions",
            "arguments": {
                "medicinalproducts": medicinalproducts,
                "patientsex": patientsex,
                "patientagegroup": patientagegroup,
                "occurcountry": occurcountry,
                "serious": serious,
                "seriousnessdeath": seriousnessdeath,
            },
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_additive_adverse_reactions"]
