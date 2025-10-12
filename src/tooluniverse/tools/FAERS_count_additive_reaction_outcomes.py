"""
FAERS_count_additive_reaction_outcomes

Additive multi-drug data: Determine reaction outcome counts (e.g., recovered, resolving, fatal) across medicinal products using standardized outcome mappings. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_additive_reaction_outcomes(
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
    Additive multi-drug data: Determine reaction outcome counts (e.g., recovered, resolving, fatal) across medicinal products using standardized outcome mappings. Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproducts : list[Any]
        Array of medicinal product names.
    patientsex : str

    patientagegroup : str

    occurcountry : str

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
            "name": "FAERS_count_additive_reaction_outcomes",
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


__all__ = ["FAERS_count_additive_reaction_outcomes"]
