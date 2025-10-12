"""
FAERS_count_death_related_by_drug

Count adverse events associated with patient death for a given drug. Data source: FDA Adverse Event Reporting System (FAERS).
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


def FAERS_count_death_related_by_drug(
    medicinalproduct: str,
    *,
    stream_callback: Optional[Callable[[str], None]] = None,
    use_cache: bool = False,
    validate: bool = True,
) -> Any:
    """
    Count adverse events associated with patient death for a given drug. Data source: FDA Adverse Event Reporting System (FAERS).

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
            "name": "FAERS_count_death_related_by_drug",
            "arguments": {"medicinalproduct": medicinalproduct},
        },
        stream_callback=stream_callback,
        use_cache=use_cache,
        validate=validate,
    )


__all__ = ["FAERS_count_death_related_by_drug"]
