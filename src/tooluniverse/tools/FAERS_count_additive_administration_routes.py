"""
FAERS_count_additive_administration_routes

Additive multi-drug data: Enumerate and count administration routes for adverse events across specified medicinal products, using standardized route codes. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_additive_administration_routes(
    medicinalproducts: list[Any],
    serious: Optional[str] = None,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Additive multi-drug data: Enumerate and count administration routes for adverse events across specified medicinal products, using standardized route codes. Data source: FDA Adverse Event Reporting System (FAERS).

    Parameters
    ----------
    medicinalproducts : list[Any]
        Array of medicinal product names.
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
            "name": "FAERS_count_additive_administration_routes",
            "arguments": {"medicinalproducts": medicinalproducts, "serious": serious},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_additive_administration_routes"]
